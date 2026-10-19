"""Entry point used by the backend: :func:`forecast_items` (FQ-13).

The backend's job runner builds the weekly history table for the items of a
run, calls :func:`forecast_items` and stores one ``forecast`` row per item and
week from ``ForecastResult.forecasts``. The package never touches the
database or HTTP: everything comes in and goes out as pandas frames and plain
Python objects.

In this version the available models are the baselines of
``forecasting.models.baselines`` and the result carries point forecasts only.
Prediction intervals (FQ-07), the minimum-history fallback (FQ-04) and
censored-demand handling for stock-out weeks (FQ-10) are planned; censored
weeks are already counted per item so that the backend can report them.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping

import numpy as np
import pandas as pd

from forecasting.data.schema import (
    DATE,
    DEFAULT_HORIZON_WEEKS,
    IS_FILLED,
    IS_STOCK_OUT,
    ITEM_CODE,
    MAX_HORIZON_WEEKS,
    MIN_HORIZON_WEEKS,
    PERIOD_START,
    QUANTITY,
)
from forecasting.data.validation import make_regular_weekly, validate_consumption, weekly_index
from forecasting.models.baselines import make_forecaster

MODEL = "model"
POINT = "point"
FORECAST_COLUMNS = (ITEM_CODE, PERIOD_START, POINT, MODEL)
ITEM_INFO_COLUMNS = (ITEM_CODE, "n_history_weeks", "n_filled_weeks", "n_censored_weeks", MODEL)


@dataclass(frozen=True)
class ForecastConfig:
    """Configuration of one forecast run.

    ``model`` is a registry name (``naive``, ``seasonal_naive``,
    ``moving_average``, ``croston``, ``sba``), ``params`` holds its
    constructor parameters and ``horizon`` is the number of weeks to forecast
    (1 to 52, FQ-03). The configuration is validated on creation and
    serialised with :meth:`to_dict` for ``forecast_run.config_json`` (FQ-11).
    """

    model: str = "naive"
    horizon: int = DEFAULT_HORIZON_WEEKS
    params: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.horizon, bool) or not isinstance(self.horizon, (int, np.integer)):
            raise ValueError(f"horizon must be an integer, got {self.horizon!r}")
        if not MIN_HORIZON_WEEKS <= self.horizon <= MAX_HORIZON_WEEKS:
            raise ValueError(
                f"horizon must be between {MIN_HORIZON_WEEKS} and {MAX_HORIZON_WEEKS} weeks, got {self.horizon}"
            )
        object.__setattr__(self, "horizon", int(self.horizon))
        if not isinstance(self.params, Mapping):
            raise ValueError(f"params must be a mapping, got {type(self.params).__name__}")
        object.__setattr__(self, "params", dict(self.params))
        # Validates the model name and its parameters.
        make_forecaster(self.model, **self.params)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ForecastConfig":
        """Build a configuration from a mapping such as ``forecast_run.config_json``."""
        unknown = set(data) - {"model", "horizon", "params"}
        if unknown:
            raise ValueError(f"unknown configuration keys: {sorted(unknown)}")
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return {"model": self.model, "horizon": self.horizon, "params": dict(self.params)}


@dataclass(frozen=True)
class ForecastResult:
    """Output of :func:`forecast_items`.

    Attributes:
        forecasts: Tidy frame with one row per item and horizon week:
            ``item_code``, ``period_start`` (Monday of the forecast week),
            ``point`` (non-negative) and ``model`` (name of the model that
            produced the row; differs from ``model_name`` when a fallback was
            used).
        item_info: One row per item: ``item_code``, ``n_history_weeks``
            (length of the regular series the model was fitted on),
            ``n_filled_weeks`` (weeks absent from the input and filled with
            zero), ``n_censored_weeks`` (weeks flagged ``is_stock_out``) and
            ``model``.
        model_name: The configured model.
        horizon: Number of forecast weeks.
        origin: Last week of the history; forecasts start the week after.
        config: The configuration used, for ``forecast_run.config_json``.
        warnings: Messages about fallbacks and filled weeks.
    """

    forecasts: pd.DataFrame
    item_info: pd.DataFrame
    model_name: str
    horizon: int
    origin: pd.Timestamp
    config: ForecastConfig
    warnings: tuple[str, ...] = ()

    @property
    def item_codes(self) -> list[str]:
        return self.item_info[ITEM_CODE].tolist()


def _coerce_config(config: ForecastConfig | Mapping[str, Any] | None, horizon: int | None) -> ForecastConfig:
    if config is None:
        resolved = ForecastConfig()
    elif isinstance(config, ForecastConfig):
        resolved = config
    elif isinstance(config, Mapping):
        resolved = ForecastConfig.from_dict(config)
    else:
        raise TypeError(f"config must be a ForecastConfig, a mapping or None, got {type(config).__name__}")
    if horizon is not None:
        # ``replace`` re-runs the validation of ``__post_init__``.
        resolved = replace(resolved, horizon=horizon)
    return resolved


def forecast_items(
    history: pd.DataFrame,
    horizon: int | None = None,
    config: ForecastConfig | Mapping[str, Any] | None = None,
) -> ForecastResult:
    """Forecast weekly consumption for every item in ``history``.

    Args:
        history: Frame with ``item_code``, ``period_start`` and ``quantity``
            (optionally ``item_name``, ``unit`` and ``is_stock_out``), one row
            per item and week. It is validated first; on any problem a
            :class:`forecasting.data.validation.DataValidationError` is raised
            and no forecast is produced (NFR-06). Weeks missing between an
            item's first week and the last week of the frame are filled with
            zero consumption and reported in ``item_info`` and ``warnings``.
        horizon: Weeks to forecast; overrides ``config.horizon`` when given.
        config: :class:`ForecastConfig`, a mapping with the same keys, or
            ``None`` for the defaults (``naive``, 12 weeks).

    Returns:
        :class:`ForecastResult` with forecasts for the ``horizon`` Mondays
        following the last week of the history.
    """
    resolved = _coerce_config(config, horizon)
    validated = validate_consumption(history)
    regular = make_regular_weekly(validated)
    origin = regular[PERIOD_START].max()
    future = weekly_index(origin, resolved.horizon).astype(DATE)

    rows: list[pd.DataFrame] = []
    info: list[dict[str, Any]] = []
    warnings: list[str] = []
    for code, group in regular.groupby(ITEM_CODE, sort=True):
        y = group[QUANTITY].to_numpy(dtype=float)
        model = make_forecaster(resolved.model, **resolved.params).fit(y)
        # Consumption cannot be negative (FQ-07); baselines never produce
        # negatives, the clip protects against future models that could.
        point = np.maximum(model.predict(resolved.horizon), 0.0)
        used = model.name
        if getattr(model, "fallback_used_", False):
            used = "naive"
            warnings.append(
                f"{code}: {resolved.model} needs {model.season_length} weeks of history, "
                f"got {y.size}; naive forecast used"
            )
        n_censored = int(group[IS_STOCK_OUT].sum()) if IS_STOCK_OUT in group.columns else 0
        rows.append(pd.DataFrame({ITEM_CODE: code, PERIOD_START: future, POINT: point, MODEL: used}))
        info.append(
            {
                ITEM_CODE: code,
                "n_history_weeks": int(y.size),
                "n_filled_weeks": int(group[IS_FILLED].sum()),
                "n_censored_weeks": n_censored,
                MODEL: used,
            }
        )

    item_info = pd.DataFrame(info, columns=list(ITEM_INFO_COLUMNS))
    filled_items = int((item_info["n_filled_weeks"] > 0).sum())
    if filled_items:
        warnings.append(
            f"{filled_items} item(s) had {int(item_info['n_filled_weeks'].sum())} missing week(s) "
            "filled with zero consumption"
        )
    forecasts = pd.concat(rows, ignore_index=True)[list(FORECAST_COLUMNS)]
    return ForecastResult(
        forecasts=forecasts,
        item_info=item_info,
        model_name=resolved.model,
        horizon=resolved.horizon,
        origin=origin,
        config=resolved,
        warnings=tuple(warnings),
    )
