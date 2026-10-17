"""Tests for forecasting.data.validation (NFR-06, FQ-12, FR-02)."""

import numpy as np
import pandas as pd
import pytest

from forecasting.data import schema
from forecasting.data.validation import (
    DataValidationError,
    ValidationError,
    ValidationProblem,
    collect_problems,
    make_regular_weekly,
    validate_consumption,
    validate_receipts,
    validate_stock,
    weekly_index,
)

MONDAYS = ["2026-01-05", "2026-01-12", "2026-01-19", "2026-01-26"]


def consumption(**overrides) -> pd.DataFrame:
    data = {
        "item_code": ["A-1", "A-1", "A-1", "B-2"],
        "item_name": ["Amoxicillin 500 mg", "Amoxicillin 500 mg", "Amoxicillin 500 mg", "Bisoprolol 5 mg"],
        "unit": ["pack", "pack", "pack", "pack"],
        "period_start": [MONDAYS[0], MONDAYS[1], MONDAYS[2], MONDAYS[1]],
        "quantity": [3, 0, 5, 2],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def problem_by_code(error: DataValidationError, code: str) -> ValidationProblem:
    matches = [problem for problem in error.problems if problem.code == code]
    assert len(matches) == 1, f"expected one '{code}' problem, got {error.codes}"
    return matches[0]


# --------------------------------------------------------------------------
# validate_consumption: happy path
# --------------------------------------------------------------------------


def test_valid_consumption_is_normalised_and_sorted() -> None:
    raw = consumption()

    out = validate_consumption(raw)

    assert list(out.columns) == ["item_code", "period_start", "quantity", "item_name", "unit"]
    assert out["period_start"].dtype == "datetime64[ns]"
    assert out["quantity"].dtype == "float64"
    assert out["item_code"].tolist() == ["A-1", "A-1", "A-1", "B-2"]
    assert out["period_start"].tolist() == [pd.Timestamp(d) for d in (MONDAYS[0], MONDAYS[1], MONDAYS[2], MONDAYS[1])]
    assert out["quantity"].tolist() == [3.0, 0.0, 5.0, 2.0]
    assert out.index.tolist() == [0, 1, 2, 3]
    # The input frame is left untouched.
    assert raw["period_start"].dtype == object or raw["period_start"].dtype == "str"
    assert raw["quantity"].tolist() == [3, 0, 5, 2]


def test_sorting_is_by_item_then_period() -> None:
    raw = consumption(
        item_code=["B-2", "A-1", "A-1", "A-1"],
        period_start=[MONDAYS[1], MONDAYS[2], MONDAYS[0], MONDAYS[1]],
        quantity=[2, 5, 3, 0],
    )

    out = validate_consumption(raw)

    assert out["item_code"].tolist() == ["A-1", "A-1", "A-1", "B-2"]
    assert out["quantity"].tolist() == [3.0, 0.0, 5.0, 2.0]


def test_item_codes_are_stripped_and_extra_columns_are_kept() -> None:
    raw = consumption(item_code=[" A-1", "A-1 ", "A-1", "B-2"], source=["x", "x", "x", "y"])

    out = validate_consumption(raw)

    assert out["item_code"].tolist() == ["A-1", "A-1", "A-1", "B-2"]
    assert list(out.columns)[-1] == "source"


def test_collect_problems_returns_empty_list_for_valid_frame() -> None:
    assert collect_problems(consumption(), schema.CONSUMPTION) == []


def test_optional_is_stock_out_is_typed_as_bool() -> None:
    out = validate_consumption(consumption(is_stock_out=[False, True, False, False]))

    assert out["is_stock_out"].dtype == bool
    assert out["is_stock_out"].tolist() == [False, True, False, False]


# --------------------------------------------------------------------------
# validate_consumption: problems
# --------------------------------------------------------------------------


def test_missing_columns_are_reported_and_other_checks_do_not_run() -> None:
    raw = consumption(quantity=[-1, 0, 5, 2]).drop(columns=["period_start"])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    error = info.value
    assert error.codes == ("missing_column",)
    assert problem_by_code(error, "missing_column").column == "period_start"
    assert "consumption data failed validation with 1 problem(s)" in str(error)


def test_negative_quantity() -> None:
    with pytest.raises(DataValidationError) as info:
        validate_consumption(consumption(quantity=[3, -1, 5, 2]))

    problem = problem_by_code(info.value, "negative_quantity")
    assert problem.column == "quantity"
    assert problem.row_count == 1
    assert problem.examples == (1,)


def test_non_numeric_quantity() -> None:
    with pytest.raises(DataValidationError) as info:
        validate_consumption(consumption(quantity=["3", "many", "5", "2"]))

    assert problem_by_code(info.value, "non_numeric_quantity").row_count == 1


def test_missing_quantity() -> None:
    with pytest.raises(DataValidationError) as info:
        validate_consumption(consumption(quantity=[3.0, np.nan, 5.0, 2.0]))

    assert problem_by_code(info.value, "missing_quantity").examples == (1,)


def test_infinite_quantity() -> None:
    with pytest.raises(DataValidationError) as info:
        validate_consumption(consumption(quantity=[3.0, np.inf, 5.0, 2.0]))

    assert problem_by_code(info.value, "non_finite_quantity").row_count == 1


def test_duplicate_item_and_period() -> None:
    raw = consumption(period_start=[MONDAYS[0], MONDAYS[0], MONDAYS[2], MONDAYS[1]])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    problem = problem_by_code(info.value, "duplicate_period")
    assert problem.row_count == 2
    assert problem.examples == (0, 1)


def test_duplicate_detection_ignores_whitespace_around_item_code() -> None:
    raw = consumption(item_code=["A-1", " A-1", "A-1", "B-2"], period_start=[MONDAYS[0], MONDAYS[0], MONDAYS[2], MONDAYS[1]])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert "duplicate_period" in info.value.codes


def test_period_start_must_be_monday() -> None:
    raw = consumption(period_start=[MONDAYS[0], "2026-01-13", MONDAYS[2], MONDAYS[1]])  # Tuesday

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "period_not_monday").examples == (1,)


@pytest.mark.parametrize("bad_value", ["not a date", "05.01.2026", "01/05/2026", "2026-13-01"])
def test_unparsable_date(bad_value: str) -> None:
    raw = consumption(period_start=[MONDAYS[0], bad_value, MONDAYS[2], MONDAYS[1]])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "unparsable_date").examples == (1,)
    assert "unparsable_date" in info.value.codes and "period_not_monday" not in info.value.codes


def test_missing_date() -> None:
    raw = consumption(period_start=[MONDAYS[0], None, MONDAYS[2], MONDAYS[1]])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "missing_date").row_count == 1


def test_date_with_time_part_is_rejected() -> None:
    raw = consumption(period_start=[MONDAYS[0], "2026-01-12 10:30", MONDAYS[2], MONDAYS[1]])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "date_has_time").examples == (1,)


def test_missing_item_code() -> None:
    raw = consumption(item_code=["A-1", "", None, "B-2"], period_start=MONDAYS)

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "missing_item_code").row_count == 2


def test_invalid_is_stock_out_values() -> None:
    raw = consumption(is_stock_out=[False, "yes", None, True])

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    assert problem_by_code(info.value, "invalid_boolean").row_count == 2


def test_all_problems_are_reported_together() -> None:
    raw = consumption(
        period_start=[MONDAYS[0], "2026-01-13", MONDAYS[2], MONDAYS[2]],
        item_code=["A-1", "A-1", "A-1", "A-1"],
        quantity=[3, -4, 5, 2],
    )

    with pytest.raises(DataValidationError) as info:
        validate_consumption(raw)

    error = info.value
    assert set(error.codes) == {"period_not_monday", "negative_quantity", "duplicate_period"}
    assert all(isinstance(problem, ValidationProblem) for problem in error.problems)
    assert "3 problem(s)" in str(error)
    assert isinstance(error, ValueError)


def test_no_rows() -> None:
    with pytest.raises(DataValidationError) as info:
        validate_consumption(consumption().iloc[0:0])

    assert info.value.codes == ("no_rows",)


def test_not_a_dataframe() -> None:
    with pytest.raises(TypeError):
        validate_consumption([1, 2, 3])


def test_validation_error_alias() -> None:
    assert ValidationError is DataValidationError


# --------------------------------------------------------------------------
# validate_stock and validate_receipts
# --------------------------------------------------------------------------


def test_validate_stock() -> None:
    raw = pd.DataFrame(
        {
            "item_code": ["A-1", "A-1"],
            "period_start": [MONDAYS[1], MONDAYS[0]],
            "quantity_on_hand": [0, 12],
        }
    )

    out = validate_stock(raw)

    assert list(out.columns) == ["item_code", "period_start", "quantity_on_hand"]
    assert out["quantity_on_hand"].tolist() == [12.0, 0.0]

    with pytest.raises(DataValidationError) as info:
        validate_stock(raw.rename(columns={"quantity_on_hand": "quantity"}))
    assert problem_by_code(info.value, "missing_column").column == "quantity_on_hand"


def test_validate_receipts_allows_any_weekday_and_repeated_deliveries() -> None:
    raw = pd.DataFrame(
        {
            "item_code": ["A-1", "A-1", "B-2"],
            "received_on": ["2026-01-07", "2026-01-07", "2026-01-09"],  # Wednesday, Friday
            "quantity": [100, 50, 20],
            "supplier": ["SK-Pharmacy", "SK-Pharmacy", None],
        }
    )

    out = validate_receipts(raw)

    assert len(out) == 3
    assert out["received_on"].dtype == "datetime64[ns]"
    assert out["quantity"].tolist() == [100.0, 50.0, 20.0]


def test_validate_receipts_rejects_negative_and_bad_dates() -> None:
    raw = pd.DataFrame({"item_code": ["A-1", "B-2"], "received_on": ["2026-01-07", "soon"], "quantity": [-5, 1]})

    with pytest.raises(DataValidationError) as info:
        validate_receipts(raw)

    assert set(info.value.codes) == {"unparsable_date", "negative_quantity"}


# --------------------------------------------------------------------------
# make_regular_weekly
# --------------------------------------------------------------------------


def test_make_regular_weekly_fills_missing_weeks_with_zero_and_flags_them() -> None:
    raw = consumption(
        item_code=["A-1", "A-1", "B-2", "B-2"],
        period_start=[MONDAYS[0], MONDAYS[2], MONDAYS[1], MONDAYS[3]],
        quantity=[3, 5, 2, 4],
        is_stock_out=[False, True, False, False],
    )

    out = make_regular_weekly(validate_consumption(raw))

    assert list(out.columns) == ["item_code", "period_start", "quantity", "item_name", "unit", "is_stock_out", "is_filled"]
    a = out[out["item_code"] == "A-1"]
    b = out[out["item_code"] == "B-2"]
    # A-1 runs from its first week to the global last week (2026-01-26).
    assert a["period_start"].tolist() == [pd.Timestamp(d) for d in MONDAYS]
    assert a["quantity"].tolist() == [3.0, 0.0, 5.0, 0.0]
    assert a["is_filled"].tolist() == [False, True, False, True]
    assert a["is_stock_out"].tolist() == [False, False, True, False]
    assert a["item_name"].tolist() == ["Amoxicillin 500 mg"] * 4
    # B-2 starts with its own first week.
    assert b["period_start"].tolist() == [pd.Timestamp(d) for d in MONDAYS[1:]]
    assert b["quantity"].tolist() == [2.0, 0.0, 4.0]
    assert b["is_filled"].tolist() == [False, True, False]
    assert out["is_filled"].dtype == bool
    assert out["is_stock_out"].dtype == bool
    assert out.index.tolist() == list(range(len(out)))


def test_make_regular_weekly_series_are_contiguous() -> None:
    raw = consumption(
        item_code=["A-1", "A-1", "B-2", "B-2"],
        period_start=[MONDAYS[0], MONDAYS[3], MONDAYS[1], MONDAYS[2]],
        quantity=[1, 1, 1, 1],
    )

    out = make_regular_weekly(validate_consumption(raw))

    for _, group in out.groupby("item_code"):
        steps = group["period_start"].diff().dropna().unique().tolist()
        assert steps == [pd.Timedelta(days=7)]


def test_make_regular_weekly_end_extends_every_item() -> None:
    out = make_regular_weekly(validate_consumption(consumption()), end="2026-02-02")

    assert out["period_start"].max() == pd.Timestamp("2026-02-02")
    assert out[out["item_code"] == "B-2"]["is_filled"].tolist() == [False, True, True, True]
    assert out[out["item_code"] == "B-2"]["quantity"].sum() == 2.0


def test_make_regular_weekly_rejects_end_that_is_not_monday() -> None:
    with pytest.raises(ValueError, match="Monday"):
        make_regular_weekly(validate_consumption(consumption()), end="2026-02-03")


def test_make_regular_weekly_omits_items_starting_after_end() -> None:
    out = make_regular_weekly(validate_consumption(consumption()), end=MONDAYS[0])

    assert out["item_code"].unique().tolist() == ["A-1"]
    assert len(out) == 1


def test_make_regular_weekly_uses_quantity_on_hand_for_stock_frames() -> None:
    raw = pd.DataFrame({"item_code": ["A-1", "A-1"], "period_start": [MONDAYS[0], MONDAYS[2]], "quantity_on_hand": [12, 0]})

    out = make_regular_weekly(validate_stock(raw))

    assert out["quantity_on_hand"].tolist() == [12.0, 0.0, 0.0]
    assert out["is_filled"].tolist() == [False, True, False]


def test_make_regular_weekly_custom_fill_value_and_flag_column() -> None:
    out = make_regular_weekly(validate_consumption(consumption()), fill_value=np.nan, flag_column="missing")

    assert "missing" in out.columns
    assert out.loc[out["missing"], "quantity"].isna().all()


def test_make_regular_weekly_requires_validated_input() -> None:
    raw = consumption()  # period_start still a string column

    with pytest.raises(ValueError, match="validate the frame first"):
        make_regular_weekly(raw)

    duplicated = validate_consumption(raw)
    duplicated = pd.concat([duplicated, duplicated.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        make_regular_weekly(duplicated)

    with pytest.raises(ValueError, match="missing"):
        make_regular_weekly(validate_consumption(raw).drop(columns=["quantity"]))


def test_make_regular_weekly_on_empty_frame() -> None:
    empty = validate_consumption(consumption()).iloc[0:0]

    out = make_regular_weekly(empty)

    assert len(out) == 0
    assert "is_filled" in out.columns


def test_make_regular_weekly_is_idempotent_on_its_own_output() -> None:
    raw = consumption(
        item_code=["A-1", "A-1", "B-2", "B-2"],
        period_start=[MONDAYS[0], MONDAYS[2], MONDAYS[1], MONDAYS[3]],
        quantity=[3, 5, 2, 4],
        is_stock_out=[False, True, False, False],
    )
    once = make_regular_weekly(validate_consumption(raw))

    twice = make_regular_weekly(once)

    # Regression: the flag column used to be copied twice on a second call.
    assert list(twice.columns) == list(once.columns)
    assert list(twice.columns).count("is_filled") == 1
    assert twice["is_filled"].dtype == bool
    # The grid is complete after the first call, so the recomputed flag is
    # False everywhere and the data columns are unchanged.
    assert not twice["is_filled"].any()
    pd.testing.assert_frame_equal(twice.drop(columns=["is_filled"]), once.drop(columns=["is_filled"]))

    # The same holds when the output is validated again first, as the API does.
    revalidated = make_regular_weekly(validate_consumption(once))
    assert list(revalidated.columns) == list(once.columns)

    empty_twice = make_regular_weekly(make_regular_weekly(once.iloc[0:0]))
    assert list(empty_twice.columns) == list(once.columns)


def test_weekly_index_starts_the_week_after_origin() -> None:
    index = weekly_index(pd.Timestamp("2026-01-26"), periods=3)

    assert index.tolist() == [pd.Timestamp("2026-02-02"), pd.Timestamp("2026-02-09"), pd.Timestamp("2026-02-16")]
