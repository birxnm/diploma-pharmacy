"""Tests for forecasting.evaluation.metrics (FQ-08)."""

import json

import numpy as np
import pandas as pd
import pytest

from forecasting.evaluation import bias, mae, summarise, wape

ACTUAL = [1, 2, 3, 4]
PREDICTED = [1, 3, 1, 4]  # absolute errors 0, 1, 2, 0


def test_mae_hand_computed() -> None:
    assert mae(ACTUAL, PREDICTED) == pytest.approx(3 / 4)


def test_wape_hand_computed() -> None:
    assert wape(ACTUAL, PREDICTED) == pytest.approx(3 / 10)


def test_wape_is_none_when_actuals_sum_to_zero() -> None:
    assert wape([0, 0, 0], [1, 0, 2]) is None
    assert mae([0, 0, 0], [1, 0, 2]) == pytest.approx(1.0)


def test_bias_sign_convention() -> None:
    assert bias([2, 2], [3, 1]) == 0.0
    assert bias([2, 2], [3, 3]) == 1.0  # over-forecast is positive
    assert bias([2, 2], [1, 1]) == -1.0


def test_perfect_forecast() -> None:
    assert mae(ACTUAL, ACTUAL) == 0.0
    assert wape(ACTUAL, ACTUAL) == 0.0
    assert bias(ACTUAL, ACTUAL) == 0.0


def test_metrics_return_plain_python_floats() -> None:
    for value in (mae(ACTUAL, PREDICTED), wape(ACTUAL, PREDICTED), bias(ACTUAL, PREDICTED)):
        assert type(value) is float


def test_summarise_contents_are_json_serialisable() -> None:
    summary = summarise(ACTUAL, PREDICTED)

    assert summary == {
        "n_periods": 4,
        "actual_total": 10.0,
        "predicted_total": 9.0,
        "mae": pytest.approx(0.75),
        "wape": pytest.approx(0.3),
        "bias": pytest.approx(-0.25),
    }
    assert json.loads(json.dumps(summary))["n_periods"] == 4
    assert json.loads(json.dumps(summarise([0, 0], [1, 1])))["wape"] is None


def test_pooled_wape_is_not_the_average_of_per_item_wape() -> None:
    actual_a, predicted_a = [10, 10], [12, 12]  # WAPE 0.2
    actual_b, predicted_b = [1, 1], [2, 2]  # WAPE 1.0

    pooled = summarise(actual_a + actual_b, predicted_a + predicted_b)

    assert pooled["wape"] == pytest.approx(6 / 22)
    assert pooled["wape"] != pytest.approx((0.2 + 1.0) / 2)


def test_accepts_series_and_arrays() -> None:
    actual = pd.Series(ACTUAL, index=[10, 11, 12, 13])
    predicted = np.array(PREDICTED, dtype=float)

    assert mae(actual, predicted) == pytest.approx(0.75)


@pytest.mark.parametrize(
    ("actual", "predicted"),
    [
        ([1, 2, 3], [1, 2]),
        ([], []),
        ([[1, 2]], [[1, 2]]),
        ([1, np.nan], [1, 1]),
        ([1, 1], [1, np.inf]),
        (["a", "b"], [1, 2]),
    ],
    ids=["length-mismatch", "empty", "two-dimensional", "nan", "inf", "non-numeric"],
)
@pytest.mark.parametrize("metric", [mae, wape, bias, summarise])
def test_invalid_input_is_rejected(metric, actual, predicted) -> None:
    with pytest.raises(ValueError):
        metric(actual, predicted)
