"""Tests for forecasting.api.forecast_items with a tiny in-memory history (FQ-12, FQ-13)."""

import pandas as pd
import pytest

from forecasting.api import FORECAST_COLUMNS, ITEM_INFO_COLUMNS, ForecastConfig, ForecastResult, forecast_items
from forecasting.data.validation import DataValidationError

MONDAYS = pd.date_range("2026-01-05", periods=6, freq="W-MON")  # 2026-01-05 .. 2026-02-09


def history() -> pd.DataFrame:
    """Two items: A-1 has six consecutive weeks, B-2 has a gap in week 4."""
    rows = [("A-1", week, quantity) for week, quantity in zip(MONDAYS, [1, 2, 3, 4, 5, 6])]
    rows += [("B-2", MONDAYS[1], 2), ("B-2", MONDAYS[2], 0), ("B-2", MONDAYS[4], 4), ("B-2", MONDAYS[5], 2)]
    return pd.DataFrame(rows, columns=["item_code", "period_start", "quantity"])


def test_naive_forecast_rows_dates_and_values() -> None:
    result = forecast_items(history(), horizon=3, config=ForecastConfig(model="naive"))

    assert isinstance(result, ForecastResult)
    forecasts = result.forecasts
    assert list(forecasts.columns) == list(FORECAST_COLUMNS) == ["item_code", "period_start", "point", "model"]
    assert len(forecasts) == 6
    assert result.origin == MONDAYS[-1]
    expected_weeks = [MONDAYS[-1] + pd.Timedelta(days=7 * step) for step in (1, 2, 3)]
    a = forecasts[forecasts["item_code"] == "A-1"]
    b = forecasts[forecasts["item_code"] == "B-2"]
    assert a["period_start"].tolist() == expected_weeks
    assert b["period_start"].tolist() == expected_weeks
    assert a["point"].tolist() == [6.0, 6.0, 6.0]
    assert b["point"].tolist() == [2.0, 2.0, 2.0]
    assert (forecasts["model"] == "naive").all()
    assert forecasts["point"].dtype == "float64"
    assert forecasts["period_start"].dtype == "datetime64[ns]"
    assert result.model_name == "naive"
    assert result.horizon == 3
    assert result.item_codes == ["A-1", "B-2"]


def test_missing_weeks_are_filled_with_zero_before_fitting() -> None:
    config = ForecastConfig(model="moving_average", params={"window": 4})

    result = forecast_items(history(), config=config)  # horizon from the config: 12 weeks

    b = result.forecasts[result.forecasts["item_code"] == "B-2"]
    # Regular series of B-2: 2, 0, 0 (filled), 4, 2 -> mean of the last four = 1.5
    assert len(b) == 12
    assert b["point"].tolist() == pytest.approx([1.5] * 12)
    info = result.item_info.set_index("item_code")
    assert list(result.item_info.columns) == list(ITEM_INFO_COLUMNS)
    assert info.loc["B-2", "n_history_weeks"] == 5
    assert info.loc["B-2", "n_filled_weeks"] == 1
    assert info.loc["A-1", "n_filled_weeks"] == 0
    assert any("filled with zero" in warning for warning in result.warnings)


def test_config_as_mapping_and_horizon_argument_override() -> None:
    result = forecast_items(history(), 2, {"model": "sba", "params": {"alpha": 0.2}, "horizon": 10})

    assert result.horizon == 2
    assert len(result.forecasts) == 4
    assert result.config.to_dict() == {"model": "sba", "horizon": 2, "params": {"alpha": 0.2}}
    assert (result.forecasts["model"] == "sba").all()


def test_default_configuration_is_naive_for_twelve_weeks() -> None:
    result = forecast_items(history())

    assert result.config == ForecastConfig()
    assert result.config.to_dict() == {"model": "naive", "horizon": 12, "params": {}}
    assert len(result.forecasts) == 24


def test_seasonal_naive_falls_back_to_naive_on_short_history() -> None:
    result = forecast_items(history(), horizon=2, config={"model": "seasonal_naive"})

    assert result.model_name == "seasonal_naive"
    assert (result.forecasts["model"] == "naive").all()
    assert (result.item_info["model"] == "naive").all()
    assert sum("naive forecast used" in warning for warning in result.warnings) == 2


def test_censored_weeks_are_counted_per_item() -> None:
    frame = history()
    frame["is_stock_out"] = [False, False, True, True, False, False, False, False, True, False]

    result = forecast_items(frame, horizon=1)

    info = result.item_info.set_index("item_code")
    assert info.loc["A-1", "n_censored_weeks"] == 2
    assert info.loc["B-2", "n_censored_weeks"] == 1


def test_forecasts_are_sorted_and_non_negative() -> None:
    frame = history()
    frame["item_code"] = frame["item_code"].map({"A-1": "Z-9", "B-2": "A-1"})

    result = forecast_items(frame, horizon=3, config={"model": "croston"})

    forecasts = result.forecasts
    assert forecasts["item_code"].tolist() == ["A-1"] * 3 + ["Z-9"] * 3
    assert forecasts.groupby("item_code")["period_start"].apply(lambda s: s.is_monotonic_increasing).all()
    assert (forecasts["point"] >= 0).all()


def test_invalid_history_raises_and_produces_nothing() -> None:
    bad = history()
    bad.loc[0, "quantity"] = -1

    with pytest.raises(DataValidationError) as info:
        forecast_items(bad, horizon=3)
    assert "negative_quantity" in info.value.codes

    with pytest.raises(DataValidationError) as info:
        forecast_items(history().drop(columns=["quantity"]), horizon=3)
    assert info.value.codes == ("missing_column",)


@pytest.mark.parametrize("horizon", [0, 53, 1.5, "4", True])
def test_invalid_horizon_is_rejected(horizon) -> None:
    with pytest.raises(ValueError, match="horizon"):
        forecast_items(history(), horizon=horizon)
    with pytest.raises(ValueError, match="horizon"):
        ForecastConfig(horizon=horizon)


def test_invalid_configuration_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown forecaster"):
        ForecastConfig(model="prophet")
    with pytest.raises(ValueError, match="invalid parameters"):
        ForecastConfig(model="naive", params={"window": 3})
    with pytest.raises(ValueError, match="alpha"):
        ForecastConfig(model="croston", params={"alpha": 2})
    with pytest.raises(ValueError, match="unknown configuration keys"):
        ForecastConfig.from_dict({"model": "naive", "seed": 42})
    with pytest.raises(ValueError, match="params must be a mapping"):
        ForecastConfig(params=[1, 2])
    with pytest.raises(TypeError):
        forecast_items(history(), config="naive")


def test_input_frame_is_not_modified() -> None:
    frame = history()
    before = frame.copy()

    forecast_items(frame, horizon=2)

    pd.testing.assert_frame_equal(frame, before)
