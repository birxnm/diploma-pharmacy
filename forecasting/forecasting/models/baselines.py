"""Baseline forecasters for weekly consumption series (FQ-05).

Every baseline works on a one-dimensional NumPy array of non-negative weekly
quantities ordered in time and returns a point forecast for each of the next
``horizon`` weeks. They are deliberately simple: they are the reference that
every candidate model has to beat (FR-16) and the fallback when an item has
too little history (FQ-04). Only NumPy is used.

Usage::

    model = make_forecaster("croston", alpha=0.1).fit(y)
    point = model.predict(horizon=12)

All forecasters reject malformed input with a ``ValueError`` (NFR-06): the
history must be one-dimensional, non-empty, finite and non-negative, and the
horizon a positive integer.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import numpy as np
from numpy.typing import ArrayLike


@runtime_checkable
class Forecaster(Protocol):
    """Interface implemented by every model in the package.

    ``fit`` consumes the history of one item and returns the forecaster so
    that calls can be chained; ``predict`` returns a float array of shape
    ``(horizon,)``; ``get_params`` returns the constructor parameters as a
    JSON-serialisable dictionary for ``forecast_run.config_json``.
    """

    name: str

    def fit(self, y: ArrayLike) -> "Forecaster": ...

    def predict(self, horizon: int) -> np.ndarray: ...

    def get_params(self) -> dict[str, Any]: ...


# --------------------------------------------------------------------------
# Input validation
# --------------------------------------------------------------------------


def check_history(y: ArrayLike) -> np.ndarray:
    """Return ``y`` as a new float array, or raise ``ValueError``."""
    try:
        history = np.array(y, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"history must be numeric: {exc}") from None
    if history.ndim != 1:
        raise ValueError(f"history must be one-dimensional, got shape {history.shape}")
    if history.size == 0:
        raise ValueError("history must contain at least one observation")
    if not np.all(np.isfinite(history)):
        raise ValueError("history contains NaN or infinite values")
    if np.any(history < 0):
        raise ValueError("history contains negative values")
    return history


def check_horizon(horizon: int) -> int:
    """Return ``horizon`` as an int, or raise ``ValueError``."""
    if isinstance(horizon, bool) or not isinstance(horizon, (int, np.integer)):
        raise ValueError(f"horizon must be a positive integer, got {horizon!r}")
    if horizon < 1:
        raise ValueError(f"horizon must be at least 1, got {horizon}")
    return int(horizon)


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return int(value)


def _smoothing_factor(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)):
        raise ValueError(f"{name} must be a number in (0, 1], got {value!r}")
    if not 0 < value <= 1:
        raise ValueError(f"{name} must be in (0, 1], got {value!r}")
    return float(value)


# --------------------------------------------------------------------------
# Baselines
# --------------------------------------------------------------------------


class _Baseline:
    """Shared fitting state, parameter reporting and representation."""

    name = "baseline"

    def __init__(self) -> None:
        self.n_obs_: int | None = None

    @property
    def is_fitted(self) -> bool:
        return self.n_obs_ is not None

    def _require_fitted(self) -> None:
        if not self.is_fitted:
            raise RuntimeError(f"{self.name} forecaster must be fitted before predict()")

    def get_params(self) -> dict[str, Any]:
        return {}

    def __repr__(self) -> str:
        params = ", ".join(f"{key}={value!r}" for key, value in self.get_params().items())
        return f"{type(self).__name__}({params})"


class NaiveForecaster(_Baseline):
    """Repeats the last observed value (``naive``)."""

    name = "naive"

    def fit(self, y: ArrayLike) -> "NaiveForecaster":
        history = check_history(y)
        self.n_obs_ = history.size
        self.level_ = float(history[-1])
        return self

    def predict(self, horizon: int) -> np.ndarray:
        steps = check_horizon(horizon)
        self._require_fitted()
        return np.full(steps, self.level_, dtype=float)


class SeasonalNaiveForecaster(_Baseline):
    """Repeats the value observed one season earlier (``seasonal_naive``).

    With weekly data and ``season_length=52`` the forecast for a week is the
    quantity of the same week one year before. When the history is shorter
    than one season there is no such value and the forecaster falls back to
    the naive forecast; ``fallback_used_`` records this (FQ-04).
    """

    name = "seasonal_naive"

    def __init__(self, season_length: int = 52) -> None:
        super().__init__()
        self.season_length = _positive_int(season_length, "season_length")

    def get_params(self) -> dict[str, Any]:
        return {"season_length": self.season_length}

    def fit(self, y: ArrayLike) -> "SeasonalNaiveForecaster":
        history = check_history(y)
        self.n_obs_ = history.size
        self.fallback_used_ = history.size < self.season_length
        self.pattern_ = history[-1:] if self.fallback_used_ else history[-self.season_length :]
        return self

    def predict(self, horizon: int) -> np.ndarray:
        steps = check_horizon(horizon)
        self._require_fitted()
        # np.resize repeats the pattern cyclically until ``steps`` values exist.
        return np.resize(self.pattern_, steps).astype(float)


class MovingAverageForecaster(_Baseline):
    """Mean of the last ``window`` observations (``moving_average``).

    The default window of 8 weeks is the project default (FQ-05). When the
    history is shorter than the window, the mean of all observations is used.
    """

    name = "moving_average"

    def __init__(self, window: int = 8) -> None:
        super().__init__()
        self.window = _positive_int(window, "window")

    def get_params(self) -> dict[str, Any]:
        return {"window": self.window}

    def fit(self, y: ArrayLike) -> "MovingAverageForecaster":
        history = check_history(y)
        self.n_obs_ = history.size
        self.n_used_ = min(self.window, history.size)
        self.level_ = float(history[-self.n_used_ :].mean())
        return self

    def predict(self, horizon: int) -> np.ndarray:
        steps = check_horizon(horizon)
        self._require_fitted()
        return np.full(steps, self.level_, dtype=float)


class CrostonForecaster(_Baseline):
    """Croston's method for intermittent demand (``croston``).

    The series is split into the sizes of the non-zero demands and the
    intervals between them, in periods, the first interval counted from the
    start of the series. Both are smoothed with simple exponential smoothing
    with the same ``alpha``, initialised with their first values. The forecast
    is the constant demand rate ``size / interval`` for every horizon step. A
    series without any demand gives a zero forecast.
    """

    name = "croston"

    def __init__(self, alpha: float = 0.1) -> None:
        super().__init__()
        self.alpha = _smoothing_factor(alpha, "alpha")

    def get_params(self) -> dict[str, Any]:
        return {"alpha": self.alpha}

    def bias_correction(self) -> float:
        """Multiplier applied to the demand rate; 1 for the classic method."""
        return 1.0

    def fit(self, y: ArrayLike) -> "CrostonForecaster":
        history = check_history(y)
        self.n_obs_ = history.size
        demand_index = np.flatnonzero(history > 0)
        self.n_demands_ = int(demand_index.size)
        if demand_index.size == 0:
            self.demand_size_ = 0.0
            self.demand_interval_ = float(history.size)
            self.rate_ = 0.0
            return self
        sizes = history[demand_index]
        intervals = np.diff(demand_index, prepend=-1).astype(float)
        size, interval = float(sizes[0]), float(intervals[0])
        for next_size, next_interval in zip(sizes[1:], intervals[1:]):
            size += self.alpha * (next_size - size)
            interval += self.alpha * (next_interval - interval)
        self.demand_size_ = size
        self.demand_interval_ = interval
        self.rate_ = size / interval
        return self

    def predict(self, horizon: int) -> np.ndarray:
        steps = check_horizon(horizon)
        self._require_fitted()
        return np.full(steps, self.bias_correction() * self.rate_, dtype=float)


class SBAForecaster(CrostonForecaster):
    """Syntetos–Boylan approximation (``sba``).

    Croston's forecast multiplied by ``1 - alpha / 2``, which removes the
    positive bias of the classic method.
    """

    name = "sba"

    def bias_correction(self) -> float:
        return 1.0 - self.alpha / 2


# --------------------------------------------------------------------------
# Registry
# --------------------------------------------------------------------------

BASELINES: dict[str, type[_Baseline]] = {
    cls.name: cls
    for cls in (
        NaiveForecaster,
        SeasonalNaiveForecaster,
        MovingAverageForecaster,
        CrostonForecaster,
        SBAForecaster,
    )
}
BASELINE_NAMES: tuple[str, ...] = tuple(BASELINES)


def make_forecaster(name: str, **params: Any) -> Forecaster:
    """Create a forecaster by its registry name, for example ``"sba"``."""
    try:
        cls = BASELINES[name]
    except KeyError:
        raise ValueError(
            f"unknown forecaster {name!r}; expected one of {', '.join(BASELINE_NAMES)}"
        ) from None
    try:
        return cls(**params)
    except TypeError as exc:
        raise ValueError(f"invalid parameters for {name!r}: {exc}") from None
