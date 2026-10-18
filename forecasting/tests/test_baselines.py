"""Tests for forecasting.models.baselines with hand-computed expectations (FQ-05)."""

import numpy as np
import pytest

from forecasting.models import (
    BASELINE_NAMES,
    BASELINES,
    CrostonForecaster,
    Forecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SBAForecaster,
    SeasonalNaiveForecaster,
    check_history,
    check_horizon,
    make_forecaster,
)

# Demand of 3 in week 3 and of 5 in week 7 (1-based): sizes 3, 5; intervals 3, 4.
INTERMITTENT = [0, 0, 3, 0, 0, 0, 5, 0]


# --------------------------------------------------------------------------
# Naive and seasonal naive
# --------------------------------------------------------------------------


def test_naive_repeats_last_value() -> None:
    point = NaiveForecaster().fit([1, 2, 3]).predict(2)

    np.testing.assert_array_equal(point, [3.0, 3.0])


def test_seasonal_naive_repeats_last_season() -> None:
    model = SeasonalNaiveForecaster(season_length=3).fit([1, 2, 3, 4, 5, 6, 7])

    np.testing.assert_array_equal(model.predict(5), [5.0, 6.0, 7.0, 5.0, 6.0])
    assert model.fallback_used_ is False


def test_seasonal_naive_with_exactly_one_season() -> None:
    model = SeasonalNaiveForecaster(season_length=3).fit([4, 5, 6])

    np.testing.assert_array_equal(model.predict(4), [4.0, 5.0, 6.0, 4.0])
    assert model.fallback_used_ is False


def test_seasonal_naive_falls_back_to_naive_when_history_is_short() -> None:
    model = SeasonalNaiveForecaster().fit([1, 2, 3])  # default season of 52 weeks

    assert model.season_length == 52
    assert model.fallback_used_ is True
    np.testing.assert_array_equal(model.predict(2), [3.0, 3.0])


# --------------------------------------------------------------------------
# Moving average
# --------------------------------------------------------------------------


def test_moving_average_uses_last_window() -> None:
    point = MovingAverageForecaster(window=3).fit([1, 2, 3, 4]).predict(2)

    np.testing.assert_array_equal(point, [3.0, 3.0])


def test_moving_average_with_short_history_uses_all_observations() -> None:
    model = MovingAverageForecaster(window=10).fit([1, 2, 3, 4])

    assert model.n_used_ == 4
    np.testing.assert_array_equal(model.predict(1), [2.5])


def test_moving_average_default_window_is_eight_weeks() -> None:
    model = MovingAverageForecaster().fit(range(1, 11))  # 1..10, last eight are 3..10

    assert model.window == 8
    np.testing.assert_array_equal(model.predict(1), [6.5])


# --------------------------------------------------------------------------
# Croston and SBA
# --------------------------------------------------------------------------


def test_croston_hand_computed() -> None:
    model = CrostonForecaster(alpha=0.1).fit(INTERMITTENT)

    # size: 3 -> 3 + 0.1 * (5 - 3) = 3.2; interval: 3 -> 3 + 0.1 * (4 - 3) = 3.1
    assert model.n_demands_ == 2
    assert model.demand_size_ == pytest.approx(3.2)
    assert model.demand_interval_ == pytest.approx(3.1)
    np.testing.assert_allclose(model.predict(3), np.full(3, 3.2 / 3.1))


def test_sba_applies_bias_correction() -> None:
    model = SBAForecaster(alpha=0.1).fit(INTERMITTENT)

    expected = (1 - 0.1 / 2) * 3.2 / 3.1
    np.testing.assert_allclose(model.predict(2), [expected, expected])
    assert model.predict(1)[0] < CrostonForecaster(alpha=0.1).fit(INTERMITTENT).predict(1)[0]


def test_croston_with_a_single_demand() -> None:
    model = CrostonForecaster(alpha=0.3).fit([0, 0, 4])

    assert model.demand_size_ == 4.0
    assert model.demand_interval_ == 3.0
    np.testing.assert_allclose(model.predict(1), [4 / 3])


def test_croston_regular_demand_equals_the_level() -> None:
    np.testing.assert_allclose(CrostonForecaster(alpha=0.5).fit([2, 2, 2, 2]).predict(2), [2.0, 2.0])


@pytest.mark.parametrize("cls", [CrostonForecaster, SBAForecaster])
def test_croston_all_zero_history_gives_zero_forecast(cls) -> None:
    model = cls().fit([0, 0, 0])

    assert model.n_demands_ == 0
    np.testing.assert_array_equal(model.predict(3), [0.0, 0.0, 0.0])


def test_croston_trailing_zeros_do_not_change_the_forecast() -> None:
    first = CrostonForecaster().fit(INTERMITTENT).predict(1)
    second = CrostonForecaster().fit(INTERMITTENT + [0, 0, 0]).predict(1)

    np.testing.assert_array_equal(first, second)


# --------------------------------------------------------------------------
# Common behaviour
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BASELINE_NAMES)
def test_every_baseline_returns_a_float_vector_of_the_requested_length(name: str) -> None:
    model = make_forecaster(name).fit(INTERMITTENT)

    point = model.predict(4)

    assert isinstance(model, Forecaster)
    assert point.shape == (4,)
    assert point.dtype == np.float64
    assert np.all(point >= 0)
    assert model.n_obs_ == len(INTERMITTENT)


def test_names_match_the_registry() -> None:
    assert set(BASELINE_NAMES) == {"naive", "seasonal_naive", "moving_average", "croston", "sba"}
    for name, cls in BASELINES.items():
        assert cls.name == name


@pytest.mark.parametrize(
    "bad",
    [[[1, 2], [3, 4]], [], [1, np.nan], [1, np.inf], [1, -1], ["a", "b"]],
    ids=["two-dimensional", "empty", "nan", "inf", "negative", "non-numeric"],
)
@pytest.mark.parametrize("name", BASELINE_NAMES)
def test_invalid_history_is_rejected(name: str, bad) -> None:
    with pytest.raises(ValueError):
        make_forecaster(name).fit(bad)


def test_check_history_returns_an_independent_float_copy() -> None:
    y = np.array([1.0, 2.0, 3.0])

    history = check_history(y)
    history[0] = 100.0

    assert history.dtype == np.float64
    assert y[0] == 1.0


def test_fitted_state_does_not_alias_the_input() -> None:
    y = np.array([1.0, 2.0, 3.0])
    model = SeasonalNaiveForecaster(season_length=3).fit(y)
    y[:] = 100.0

    np.testing.assert_array_equal(model.predict(3), [1.0, 2.0, 3.0])


@pytest.mark.parametrize("horizon", [0, -1, 1.5, "3", True, None])
def test_invalid_horizon_is_rejected(horizon) -> None:
    model = NaiveForecaster().fit([1.0])

    with pytest.raises(ValueError):
        model.predict(horizon)


def test_numpy_integer_horizon_is_accepted() -> None:
    assert check_horizon(np.int64(3)) == 3
    assert NaiveForecaster().fit([2.0]).predict(np.int64(2)).shape == (2,)


@pytest.mark.parametrize("name", BASELINE_NAMES)
def test_predict_before_fit_raises(name: str) -> None:
    with pytest.raises(RuntimeError, match="fitted"):
        make_forecaster(name).predict(1)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: SeasonalNaiveForecaster(season_length=0),
        lambda: SeasonalNaiveForecaster(season_length=2.5),
        lambda: MovingAverageForecaster(window=0),
        lambda: MovingAverageForecaster(window="8"),
        lambda: CrostonForecaster(alpha=0),
        lambda: CrostonForecaster(alpha=1.5),
        lambda: SBAForecaster(alpha=-0.1),
        lambda: SBAForecaster(alpha=True),
    ],
)
def test_invalid_parameters_are_rejected(factory) -> None:
    with pytest.raises(ValueError):
        factory()


def test_make_forecaster_by_name_with_parameters() -> None:
    model = make_forecaster("moving_average", window=4)

    assert isinstance(model, MovingAverageForecaster)
    assert model.get_params() == {"window": 4}
    assert make_forecaster("naive").get_params() == {}
    assert make_forecaster("seasonal_naive").get_params() == {"season_length": 52}
    assert make_forecaster("sba", alpha=0.2).get_params() == {"alpha": 0.2}


def test_make_forecaster_rejects_unknown_names_and_parameters() -> None:
    with pytest.raises(ValueError, match="unknown forecaster"):
        make_forecaster("prophet")
    with pytest.raises(ValueError, match="invalid parameters"):
        make_forecaster("naive", window=3)


def test_repr_shows_parameters() -> None:
    assert repr(CrostonForecaster(alpha=0.2)) == "CrostonForecaster(alpha=0.2)"
    assert repr(NaiveForecaster()) == "NaiveForecaster()"
