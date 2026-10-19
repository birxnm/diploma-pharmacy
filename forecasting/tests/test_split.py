"""Tests for forecasting.evaluation.split (FQ-09)."""

import dataclasses

import numpy as np
import pandas as pd
import pytest

from forecasting.evaluation import TimeSplit, Window, rolling_origin_windows, split_by_cutoff, split_frame

WEEKS = pd.date_range("2026-01-05", periods=8, freq="W-MON")  # 2026-01-05 .. 2026-02-23


# --------------------------------------------------------------------------
# split_by_cutoff and split_frame
# --------------------------------------------------------------------------


def test_split_by_cutoff_with_validation() -> None:
    split = split_by_cutoff(WEEKS, train_end="2026-01-19", validation_end="2026-02-09")

    assert isinstance(split, TimeSplit)
    assert split.sizes == {"train": 3, "validation": 3, "test": 2}
    assert split.train.tolist() == [True, True, True, False, False, False, False, False]
    assert split.validation.tolist() == [False, False, False, True, True, True, False, False]
    assert split.test.tolist() == [False, False, False, False, False, False, True, True]
    assert WEEKS[split.train].max() < WEEKS[split.validation].min() < WEEKS[split.test].min()


def test_split_by_cutoff_without_validation() -> None:
    split = split_by_cutoff(WEEKS, train_end="2026-02-02")

    assert split.sizes == {"train": 5, "validation": 0, "test": 3}
    assert split.validation_end is None
    assert not split.validation.any()


def test_split_by_cutoff_masks_follow_positions_for_several_items() -> None:
    dates = ["2026-02-23", "2026-01-05", "2026-01-05", "2026-02-23", "2026-01-26"]

    split = split_by_cutoff(dates, train_end="2026-01-26")

    assert split.train.tolist() == [False, True, True, False, True]
    assert split.test.tolist() == [True, False, False, True, False]


def test_masks_are_disjoint_and_cover_every_row() -> None:
    split = split_by_cutoff(WEEKS, train_end="2026-01-12", validation_end="2026-01-26")

    total = split.train.astype(int) + split.validation.astype(int) + split.test.astype(int)
    assert total.tolist() == [1] * len(WEEKS)


@pytest.mark.parametrize(
    ("train_end", "validation_end", "message"),
    [
        ("2026-01-19", "2026-01-19", "must be after"),
        ("2026-01-19", "2026-01-12", "must be after"),
        ("2025-12-29", None, "training part is empty"),
        ("2026-02-23", None, "test part is empty"),
        ("2026-01-19", "2026-02-23", "test part is empty"),
        ("2026-01-19", "2026-01-20", "validation part is empty"),
    ],
)
def test_split_by_cutoff_rejects_bad_cutoffs(train_end, validation_end, message) -> None:
    with pytest.raises(ValueError, match=message):
        split_by_cutoff(WEEKS, train_end, validation_end)


def test_split_by_cutoff_rejects_missing_dates() -> None:
    with pytest.raises(ValueError, match="missing"):
        split_by_cutoff(["2026-01-05", None, "2026-01-19"], train_end="2026-01-05")


def test_split_frame_returns_three_frames() -> None:
    df = pd.DataFrame(
        {
            "item_code": ["A-1"] * 8 + ["B-2"] * 8,
            "period_start": list(WEEKS) * 2,
            "quantity": range(16),
        }
    )

    train, validation, test = split_frame(df, train_end="2026-01-19", validation_end="2026-02-09")

    assert (len(train), len(validation), len(test)) == (6, 6, 4)
    assert train["period_start"].max() == pd.Timestamp("2026-01-19")
    assert validation["period_start"].min() == pd.Timestamp("2026-01-26")
    assert test["period_start"].min() == pd.Timestamp("2026-02-16")
    assert sorted(train["quantity"].tolist() + validation["quantity"].tolist() + test["quantity"].tolist()) == list(range(16))


# --------------------------------------------------------------------------
# rolling_origin_windows
# --------------------------------------------------------------------------


def test_rolling_origin_windows_hand_computed() -> None:
    windows = rolling_origin_windows(n_periods=20, horizon=4, n_windows=3, min_train=5)

    assert [window.origin for window in windows] == [8, 12, 16]
    assert windows[0].train == range(0, 8)
    assert windows[0].test == range(8, 12)
    assert windows[-1].test == range(16, 20)
    assert all(window.validation == range(window.origin, window.origin) for window in windows)


def test_windows_have_no_leakage_and_are_chronological() -> None:
    n_periods = 30
    windows = rolling_origin_windows(n_periods, horizon=5, n_windows=4, min_train=3)

    for window in windows:
        assert window.train.stop == window.validation.start
        assert window.validation.stop == window.test.start == window.origin
        assert window.history == range(0, window.origin)
        assert window.test.stop <= n_periods
        assert set(window.train).isdisjoint(window.test)
    origins = [window.origin for window in windows]
    assert origins == sorted(origins) and len(set(origins)) == len(origins)
    assert windows[-1].test.stop == n_periods
    # Default step equals the horizon: test windows do not overlap.
    for earlier, later in zip(windows, windows[1:]):
        assert earlier.test.stop == later.test.start


def test_rolling_origin_with_validation_length_matches_fq09() -> None:
    windows = rolling_origin_windows(52, horizon=12, n_windows=3, min_train=4, step=4, validation_length=12)

    assert [window.origin for window in windows] == [32, 36, 40]
    first = windows[0]
    assert first.train == range(0, 20)
    assert first.validation == range(20, 32)
    assert first.history == range(0, 32)
    assert first.test == range(32, 44)
    assert windows[-1].test == range(40, 52)


def test_rolling_origin_step_smaller_than_horizon_gives_overlapping_tests() -> None:
    windows = rolling_origin_windows(20, horizon=4, n_windows=2, min_train=1, step=2)

    assert [window.origin for window in windows] == [14, 16]
    assert set(windows[0].test) & set(windows[1].test) == {16, 17}


def test_rolling_origin_rejects_insufficient_history() -> None:
    with pytest.raises(ValueError, match="cannot hold"):
        rolling_origin_windows(20, horizon=4, n_windows=3, min_train=9)
    with pytest.raises(ValueError, match="cannot hold"):
        rolling_origin_windows(20, horizon=4, n_windows=1, min_train=10, validation_length=8)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(n_periods=0, horizon=4, n_windows=1, min_train=1),
        dict(n_periods=20, horizon=0, n_windows=1, min_train=1),
        dict(n_periods=20, horizon=4, n_windows=0, min_train=1),
        dict(n_periods=20, horizon=4, n_windows=1, min_train=0),
        dict(n_periods=20, horizon=4, n_windows=1, min_train=1, step=0),
        dict(n_periods=20, horizon=4, n_windows=1, min_train=1, validation_length=-1),
        dict(n_periods=20.0, horizon=4, n_windows=1, min_train=1),
        dict(n_periods=20, horizon=True, n_windows=1, min_train=1),
    ],
)
def test_rolling_origin_rejects_invalid_arguments(kwargs) -> None:
    with pytest.raises(ValueError):
        rolling_origin_windows(**kwargs)


def test_window_is_immutable_and_usable_as_a_key() -> None:
    window = Window(origin=8, horizon=4)

    with pytest.raises(dataclasses.FrozenInstanceError):
        window.origin = 9  # type: ignore[misc]
    assert {window: "first"}[Window(8, 4)] == "first"


def test_windows_index_a_series_without_future_values() -> None:
    y = np.arange(20, dtype=float)
    window = rolling_origin_windows(20, horizon=4, n_windows=1, min_train=5)[0]

    assert y[window.train.start : window.train.stop].max() < y[window.test.start : window.test.stop].min()
