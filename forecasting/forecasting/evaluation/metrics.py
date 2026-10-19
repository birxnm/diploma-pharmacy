"""Forecast accuracy metrics (FQ-08, FR-16).

* ``mae``  = mean(|y - y_hat|), in the item's unit of measurement;
* ``wape`` = sum(|y - y_hat|) / sum(|y|), scale-free; ``None`` when the actual
  values sum to zero, because the ratio is undefined for a window without
  consumption;
* ``bias`` = mean(y_hat - y): positive when the forecast is too high.

All functions accept one-dimensional sequences of equal length and return
plain Python floats so that results can be serialised to JSON. Pooled metrics
over several items (FQ-08) are obtained by concatenating the per-item actual
and predicted arrays before calling :func:`summarise`; they are not averages
of per-item values.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _check_pair(actual: ArrayLike, predicted: ArrayLike) -> tuple[np.ndarray, np.ndarray]:
    try:
        y = np.asarray(actual, dtype=float)
        y_hat = np.asarray(predicted, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"actual and predicted must be numeric: {exc}") from None
    if y.ndim != 1 or y_hat.ndim != 1:
        raise ValueError("actual and predicted must be one-dimensional")
    if y.shape != y_hat.shape:
        raise ValueError(f"actual and predicted must have the same length, got {y.size} and {y_hat.size}")
    if y.size == 0:
        raise ValueError("actual and predicted must not be empty")
    if not (np.all(np.isfinite(y)) and np.all(np.isfinite(y_hat))):
        raise ValueError("actual and predicted must not contain NaN or infinite values")
    return y, y_hat


def mae(actual: ArrayLike, predicted: ArrayLike) -> float:
    """Mean absolute error."""
    y, y_hat = _check_pair(actual, predicted)
    return float(np.mean(np.abs(y - y_hat)))


def wape(actual: ArrayLike, predicted: ArrayLike) -> float | None:
    """Weighted absolute percentage error, or ``None`` when the actuals sum to zero."""
    y, y_hat = _check_pair(actual, predicted)
    total = float(np.sum(np.abs(y)))
    if total == 0.0:
        return None
    return float(np.sum(np.abs(y - y_hat)) / total)


def bias(actual: ArrayLike, predicted: ArrayLike) -> float:
    """Mean error ``predicted - actual``; positive means over-forecasting."""
    y, y_hat = _check_pair(actual, predicted)
    return float(np.mean(y_hat - y))


def summarise(actual: ArrayLike, predicted: ArrayLike) -> dict[str, float | int | None]:
    """All metrics plus totals for one evaluation window, as a JSON-ready dict."""
    y, y_hat = _check_pair(actual, predicted)
    return {
        "n_periods": int(y.size),
        "actual_total": float(np.sum(y)),
        "predicted_total": float(np.sum(y_hat)),
        "mae": mae(y, y_hat),
        "wape": wape(y, y_hat),
        "bias": bias(y, y_hat),
    }
