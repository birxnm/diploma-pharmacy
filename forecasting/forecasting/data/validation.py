"""Validation of input frames and construction of regular weekly series.

The package must reject malformed input with a clear, structured error instead
of producing a wrong forecast (NFR-06, FQ-12). :func:`collect_problems` runs
every check that is still meaningful and returns all problems found, so that
an import can be reported to the user in one go (FR-02). The ``validate_*``
functions raise :class:`DataValidationError` carrying that list, or return a
normalised copy of the frame: typed columns, canonical column order, rows
sorted by key.

:func:`make_regular_weekly` turns a validated frame into a contiguous weekly
series per item: missing weeks are filled with zero and flagged in
``is_filled`` (FQ-01, FQ-02). Censored-demand handling for stock-out weeks
(FQ-10) is planned and is not part of this module yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Sequence

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_object_dtype, is_string_dtype

from forecasting.data.schema import (
    BOOL,
    CONSUMPTION,
    IS_FILLED,
    ITEM_CODE,
    MONDAY,
    PERIOD_DAYS,
    PERIOD_START,
    QUANTITY,
    QUANTITY_ON_HAND,
    RECEIPTS,
    STOCK,
    STRING,
    WEEKLY_FREQ,
    FrameSchema,
)

# Number of offending index labels kept per problem for error reports.
MAX_EXAMPLES = 10


@dataclass(frozen=True)
class ValidationProblem:
    """One problem found in an input frame.

    Attributes:
        code: Stable machine-readable code, for example ``negative_quantity``.
        message: Human-readable description.
        column: Column concerned, if any.
        row_count: Number of offending rows (0 for frame-level problems).
        examples: Index labels of up to ``MAX_EXAMPLES`` offending rows.
    """

    code: str
    message: str
    column: str | None = None
    row_count: int = 0
    examples: tuple[Hashable, ...] = ()

    def __str__(self) -> str:
        text = self.message
        if self.row_count:
            text += f" ({self.row_count} row(s)"
            if self.examples:
                text += f", e.g. index {list(self.examples)}"
            text += ")"
        return text


class DataValidationError(ValueError):
    """Raised when an input frame does not satisfy its schema.

    ``problems`` holds every problem found, in the order of the checks, so
    that the caller can report all of them at once.
    """

    def __init__(self, problems: Sequence[ValidationProblem], frame_name: str = "input") -> None:
        self.problems = list(problems)
        self.frame_name = frame_name
        summary = "; ".join(str(problem) for problem in self.problems)
        super().__init__(
            f"{frame_name} data failed validation with {len(self.problems)} problem(s): {summary}"
        )

    @property
    def codes(self) -> tuple[str, ...]:
        """Problem codes in the order they were found."""
        return tuple(problem.code for problem in self.problems)


# Name used in docs/requirements.md (FQ-12).
ValidationError = DataValidationError


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def _problem(code: str, message: str, column: str | None, mask: pd.Series) -> ValidationProblem | None:
    count = int(mask.sum())
    if count == 0:
        return None
    examples = tuple(mask.index[mask.to_numpy(dtype=bool)][:MAX_EXAMPLES].tolist())
    return ValidationProblem(code, message, column=column, row_count=count, examples=examples)


def _add(problems: list[ValidationProblem], problem: ValidationProblem | None) -> None:
    if problem is not None:
        problems.append(problem)


def _normalise_item_codes(df: pd.DataFrame, problems: list[ValidationProblem]) -> pd.Series:
    raw = df[ITEM_CODE]
    codes = raw.astype(STRING).str.strip()
    missing = raw.isna() | (codes == "")
    _add(problems, _problem("missing_item_code", "column 'item_code' has empty values", ITEM_CODE, missing))
    return codes


def _parse_dates(
    df: pd.DataFrame, column: str, must_be_monday: bool, problems: list[ValidationProblem]
) -> pd.Series:
    raw = df[column]
    # Only ISO 8601 is accepted: day-first or locale formats such as
    # 05.01.2026 would otherwise be parsed silently into a wrong date.
    parsed = pd.to_datetime(raw, errors="coerce", format="ISO8601")
    missing = raw.isna()
    _add(problems, _problem("missing_date", f"column '{column}' has missing dates", column, missing))
    unparsable = parsed.isna() & ~missing
    _add(
        problems,
        _problem(
            "unparsable_date",
            f"column '{column}' has values that are not ISO dates (YYYY-MM-DD)",
            column,
            unparsable,
        ),
    )
    valid = parsed.notna()
    has_time = valid & (parsed != parsed.dt.normalize())
    _add(
        problems,
        _problem("date_has_time", f"column '{column}' must contain dates without a time part", column, has_time),
    )
    if must_be_monday:
        not_monday = valid & (parsed.dt.weekday != MONDAY)
        _add(
            problems,
            _problem(
                "period_not_monday",
                f"column '{column}' must be the Monday of the week",
                column,
                not_monday,
            ),
        )
    return parsed


def _parse_quantities(df: pd.DataFrame, column: str, problems: list[ValidationProblem]) -> pd.Series:
    raw = df[column]
    numeric = pd.to_numeric(raw, errors="coerce")
    missing = raw.isna()
    _add(problems, _problem("missing_quantity", f"column '{column}' has missing values", column, missing))
    non_numeric = numeric.isna() & ~missing
    _add(
        problems,
        _problem("non_numeric_quantity", f"column '{column}' has values that are not numbers", column, non_numeric),
    )
    finite = pd.Series(np.isfinite(numeric.to_numpy(dtype=float)), index=raw.index)
    non_finite = numeric.notna() & ~finite
    _add(
        problems,
        _problem("non_finite_quantity", f"column '{column}' has infinite values", column, non_finite),
    )
    negative = numeric < 0
    _add(problems, _problem("negative_quantity", f"column '{column}' has negative values", column, negative))
    return numeric


def _check_booleans(df: pd.DataFrame, column: str, problems: list[ValidationProblem]) -> None:
    raw = df[column]
    invalid = ~raw.isin([True, False])
    _add(
        problems,
        _problem("invalid_boolean", f"column '{column}' must contain only True/False", column, invalid),
    )


def _check_duplicates(
    key: tuple[str, ...], converted: dict[str, pd.Series], problems: list[ValidationProblem]
) -> None:
    keys = pd.DataFrame({column: converted[column] for column in key})
    # Rows with a missing key part are reported by the other checks.
    complete = keys.notna().all(axis=1)
    duplicated = keys.duplicated(keep=False) & complete
    _add(
        problems,
        _problem(
            "duplicate_period",
            f"rows with the same ({', '.join(key)}) appear more than once",
            None,
            duplicated,
        ),
    )


def _analyse(
    df: pd.DataFrame, frame_schema: FrameSchema
) -> tuple[list[ValidationProblem], dict[str, pd.Series]]:
    """Run all checks; return the problems and the converted key columns."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"expected a pandas DataFrame, got {type(df).__name__}")

    problems: list[ValidationProblem] = []
    converted: dict[str, pd.Series] = {}

    missing = [column for column in frame_schema.required if column not in df.columns]
    for column in missing:
        problems.append(
            ValidationProblem("missing_column", f"required column '{column}' is missing", column=column)
        )
    if missing:
        # The remaining checks need the required columns.
        return problems, converted
    if len(df) == 0:
        problems.append(ValidationProblem("no_rows", "the frame contains no rows"))
        return problems, converted

    converted[ITEM_CODE] = _normalise_item_codes(df, problems)
    for column in frame_schema.date_columns:
        if column in df.columns:
            converted[column] = _parse_dates(
                df, column, column in frame_schema.week_start_columns, problems
            )
    for column in frame_schema.quantity_columns:
        if column in df.columns:
            converted[column] = _parse_quantities(df, column, problems)
    for column in frame_schema.boolean_columns:
        if column in df.columns:
            _check_booleans(df, column, problems)
    if frame_schema.key:
        _check_duplicates(frame_schema.key, converted, problems)
    return problems, converted


def collect_problems(df: pd.DataFrame, frame_schema: FrameSchema) -> list[ValidationProblem]:
    """Return every problem found in ``df`` against ``frame_schema``.

    An empty list means the frame is valid. When required columns are
    missing, only ``missing_column`` problems are reported because the other
    checks cannot run.
    """
    problems, _ = _analyse(df, frame_schema)
    return problems


def _normalise(df: pd.DataFrame, frame_schema: FrameSchema, converted: dict[str, pd.Series]) -> pd.DataFrame:
    out = df.copy()
    for column, series in converted.items():
        out[column] = series
    for column, dtype in frame_schema.dtypes.items():
        if column in out.columns:
            out[column] = out[column].astype(dtype)
    schema_columns = [column for column in frame_schema.columns if column in out.columns]
    extra_columns = [column for column in out.columns if column not in schema_columns]
    out = out[schema_columns + extra_columns]
    if frame_schema.key:
        out = out.sort_values(list(frame_schema.key), kind="stable")
    return out.reset_index(drop=True)


def validate_frame(df: pd.DataFrame, frame_schema: FrameSchema) -> pd.DataFrame:
    """Validate ``df`` against ``frame_schema`` and return a normalised copy.

    Raises:
        DataValidationError: with the full list of problems when any check
            fails. No partial result is returned (NFR-06).
    """
    problems, converted = _analyse(df, frame_schema)
    if problems:
        raise DataValidationError(problems, frame_name=frame_schema.name)
    return _normalise(df, frame_schema, converted)


def validate_consumption(df: pd.DataFrame) -> pd.DataFrame:
    """Validate a weekly consumption frame (``consumption.csv`` or the history table)."""
    return validate_frame(df, CONSUMPTION)


def validate_stock(df: pd.DataFrame) -> pd.DataFrame:
    """Validate a weekly stock frame (``stock.csv``)."""
    return validate_frame(df, STOCK)


def validate_receipts(df: pd.DataFrame) -> pd.DataFrame:
    """Validate a receipts frame (``receipts.csv``)."""
    return validate_frame(df, RECEIPTS)


# --------------------------------------------------------------------------
# Regular weekly series
# --------------------------------------------------------------------------


def _require_weekly_input(df: pd.DataFrame, value_column: str) -> None:
    """Fail early with a clear message when ``df`` was not validated first."""
    for column in (ITEM_CODE, PERIOD_START, value_column):
        if column not in df.columns:
            raise ValueError(f"column '{column}' is missing; validate the frame first")
    if not is_datetime64_any_dtype(df[PERIOD_START]):
        raise ValueError("'period_start' must be a datetime column; validate the frame first")
    if len(df) == 0:
        return
    if (df[PERIOD_START].dt.weekday != MONDAY).any():
        raise ValueError("'period_start' must be the Monday of the week; validate the frame first")
    if df.duplicated(subset=[ITEM_CODE, PERIOD_START]).any():
        raise ValueError("duplicate (item_code, period_start) rows; validate the frame first")


def make_regular_weekly(
    df: pd.DataFrame,
    *,
    value_column: str | None = None,
    end: pd.Timestamp | str | None = None,
    fill_value: float = 0.0,
    flag_column: str = IS_FILLED,
) -> pd.DataFrame:
    """Return a contiguous weekly series per item with missing weeks filled.

    For every item the result covers each Monday from the item's first week
    to ``end`` (default: the last week present anywhere in the frame, so that
    all items share the same last period). Weeks absent from the input get
    ``fill_value`` in ``value_column`` and ``True`` in ``flag_column``; rows
    taken from the input get ``False``. Boolean columns such as
    ``is_stock_out`` are ``False`` in filled rows (a filled week has no stock
    information, FQ-02); string columns such as ``item_name`` and ``unit``
    are copied from the item's other rows; other numeric columns stay NaN.

    ``df`` must come from one of the ``validate_*`` functions: ``period_start``
    is a datetime column of Mondays and (``item_code``, ``period_start``) is
    unique. ``value_column`` defaults to ``quantity`` or, for stock frames,
    ``quantity_on_hand``. Items whose first week is after ``end`` are omitted.
    The result is sorted by item and week with a fresh index. When ``df``
    already contains ``flag_column`` (for example the output of an earlier
    call), that column is dropped and recomputed from the weeks absent now,
    so the result has a single flag column and the same columns as after
    one call.
    """
    if value_column is None:
        value_column = QUANTITY if QUANTITY in df.columns else QUANTITY_ON_HAND
    _require_weekly_input(df, value_column)
    if flag_column in df.columns:
        # Output of an earlier call: the flag is recomputed below and must
        # not be carried over as data (it would be copied twice otherwise).
        df = df.drop(columns=[flag_column])

    if len(df) == 0:
        out = df.copy()
        out[flag_column] = pd.Series(dtype=BOOL)
        return out.reset_index(drop=True)

    last = df[PERIOD_START].max() if end is None else pd.Timestamp(end)
    if last.weekday() != MONDAY:
        raise ValueError(f"'end' must be a Monday, got {last.date()} (weekday {last.weekday()})")

    bool_columns = [column for column in df.columns if is_bool_dtype(df[column])]
    text_columns = [
        column
        for column in df.columns
        if column not in (ITEM_CODE, PERIOD_START)
        and (is_string_dtype(df[column]) or is_object_dtype(df[column]))
    ]

    pieces: list[pd.DataFrame] = []
    for code, group in df.groupby(ITEM_CODE, sort=True):
        index = pd.date_range(group[PERIOD_START].min(), last, freq=WEEKLY_FREQ, name=PERIOD_START)
        if len(index) == 0:
            continue
        regular = group.set_index(PERIOD_START).reindex(index)
        regular[flag_column] = regular[value_column].isna()
        regular[value_column] = regular[value_column].fillna(fill_value)
        regular[ITEM_CODE] = code
        for column in text_columns:
            regular[column] = regular[column].ffill().bfill()
        for column in bool_columns:
            regular[column] = regular[column].fillna(False).astype(BOOL)
        pieces.append(regular.reset_index())

    out = pd.concat(pieces, ignore_index=True)
    columns = [column for column in df.columns if column != flag_column] + [flag_column]
    return out[columns]


def weekly_index(start: pd.Timestamp, periods: int) -> pd.DatetimeIndex:
    """Return ``periods`` consecutive Mondays starting with the week after ``start``."""
    return pd.date_range(start + pd.Timedelta(days=PERIOD_DAYS), periods=periods, freq=WEEKLY_FREQ)
