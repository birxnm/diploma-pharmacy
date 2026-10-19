"""Time-based splits for model selection and hold-out evaluation (FQ-09).

Two tools are provided:

* :func:`split_by_cutoff` and :func:`split_frame` divide observations into
  train, validation and test parts by calendar cut-off dates, for a single
  chronological split;
* :func:`rolling_origin_windows` enumerates several forecast origins over a
  regular series of ``n_periods`` steps and returns the index ranges of the
  training, validation and test parts of each window. Training and validation
  end at the origin and the test window starts at it, so no future
  observation can leak into fitting or model selection.

Both work on dates or positions only; nothing is ever shuffled.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from forecasting.data.schema import PERIOD_START


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return int(value)


def _non_negative_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer, got {value!r}")
    return int(value)


# --------------------------------------------------------------------------
# Split by cut-off dates
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class TimeSplit:
    """Boolean masks of one chronological split, aligned by position with the input."""

    train: np.ndarray
    validation: np.ndarray
    test: np.ndarray
    train_end: pd.Timestamp
    validation_end: pd.Timestamp | None

    @property
    def sizes(self) -> dict[str, int]:
        return {
            "train": int(self.train.sum()),
            "validation": int(self.validation.sum()),
            "test": int(self.test.sum()),
        }


def split_by_cutoff(
    dates: Any,
    train_end: pd.Timestamp | str,
    validation_end: pd.Timestamp | str | None = None,
) -> TimeSplit:
    """Split observations by date.

    Train is every date on or before ``train_end``; validation every date
    after ``train_end`` and on or before ``validation_end``; test everything
    later. Without ``validation_end`` the validation mask is empty and test is
    everything after ``train_end``. ``dates`` may hold several items and any
    order; the masks follow its positions.

    Raises:
        ValueError: when the cut-offs are not increasing, when ``dates`` has
            missing values, or when the train or test part (or the validation
            part, if requested) would be empty.
    """
    stamps = pd.to_datetime(pd.Series(dates), format="ISO8601")
    if stamps.isna().any():
        raise ValueError("dates must not contain missing values")
    train_end = pd.Timestamp(train_end)
    validation_end = None if validation_end is None else pd.Timestamp(validation_end)
    if validation_end is not None and validation_end <= train_end:
        raise ValueError(f"validation_end ({validation_end.date()}) must be after train_end ({train_end.date()})")

    train = (stamps <= train_end).to_numpy(dtype=bool)
    if validation_end is None:
        validation = np.zeros(len(stamps), dtype=bool)
        test = (stamps > train_end).to_numpy(dtype=bool)
    else:
        validation = ((stamps > train_end) & (stamps <= validation_end)).to_numpy(dtype=bool)
        test = (stamps > validation_end).to_numpy(dtype=bool)

    if not train.any():
        raise ValueError(f"training part is empty: no dates on or before {train_end.date()}")
    if validation_end is not None and not validation.any():
        raise ValueError(
            f"validation part is empty: no dates after {train_end.date()} and on or before {validation_end.date()}"
        )
    if not test.any():
        last_cutoff = train_end if validation_end is None else validation_end
        raise ValueError(f"test part is empty: no dates after {last_cutoff.date()}")
    return TimeSplit(train, validation, test, train_end, validation_end)


def split_frame(
    df: pd.DataFrame,
    train_end: pd.Timestamp | str,
    validation_end: pd.Timestamp | str | None = None,
    date_column: str = PERIOD_START,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return the train, validation and test rows of ``df`` split by ``date_column``."""
    split = split_by_cutoff(df[date_column], train_end, validation_end)
    return df[split.train], df[split.validation], df[split.test]


# --------------------------------------------------------------------------
# Rolling-origin windows
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Window:
    """Index ranges of one rolling-origin window over positions ``0 .. n_periods - 1``.

    ``origin`` is the position of the first test period. ``history`` is
    everything before the origin; it is divided into ``train`` and the last
    ``validation_length`` periods as ``validation``. ``test`` is the
    ``horizon`` periods starting at the origin. All ranges are half-open.
    """

    origin: int
    horizon: int
    validation_length: int = 0

    @property
    def history(self) -> range:
        return range(0, self.origin)

    @property
    def train(self) -> range:
        return range(0, self.origin - self.validation_length)

    @property
    def validation(self) -> range:
        return range(self.origin - self.validation_length, self.origin)

    @property
    def test(self) -> range:
        return range(self.origin, self.origin + self.horizon)


def rolling_origin_windows(
    n_periods: int,
    horizon: int,
    n_windows: int,
    min_train: int,
    *,
    step: int | None = None,
    validation_length: int = 0,
) -> list[Window]:
    """Return ``n_windows`` windows over a regular series of ``n_periods`` steps.

    The last test window ends exactly at ``n_periods``; earlier origins are
    ``step`` periods apart (default ``horizon``, so test windows do not
    overlap; FQ-09 uses ``step=4`` with a 12-week horizon). Every window keeps
    at least ``min_train`` training periods before its validation part. The
    windows are returned in chronological order.

    Raises:
        ValueError: when the series is too short for the requested windows.
    """
    n_periods = _positive_int(n_periods, "n_periods")
    horizon = _positive_int(horizon, "horizon")
    n_windows = _positive_int(n_windows, "n_windows")
    min_train = _positive_int(min_train, "min_train")
    step = horizon if step is None else _positive_int(step, "step")
    validation_length = _non_negative_int(validation_length, "validation_length")

    last_origin = n_periods - horizon
    origins = [last_origin - k * step for k in reversed(range(n_windows))]
    earliest_train = origins[0] - validation_length
    if earliest_train < min_train:
        raise ValueError(
            f"{n_periods} periods cannot hold {n_windows} window(s) with horizon {horizon}, "
            f"step {step}, validation length {validation_length} and at least {min_train} "
            f"training periods (the earliest window would leave {earliest_train})"
        )
    return [Window(origin, horizon, validation_length) for origin in origins]
