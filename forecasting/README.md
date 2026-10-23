# Forecasting Module

_PHA2-6 · Last updated: 2026-10-23 · Author: Evelina Penkova_

This directory contains the data preparation code and the demand forecasting
models of PharmaStock, the smart supply chain analytics system for
pharmaceutical inventory. The module predicts weekly medicine consumption per
item over a configurable horizon and provides the forecasts that the backend
turns into shortage risk (FR-06, FR-07, FR-08, FR-16, FR-17).

**Owner:** Evelina Penkova (data preparation, forecasting models, experiments)

Status on 2026-10-23: the package `forecasting/forecasting/` with input
validation, the five baselines, the metrics, the time-based split and the entry
point `forecast_items` is merged (PHA2-16, 194 tests); the synthetic development
dataset and its generator are merged (PHA2-15); the experiment runner for the
baseline comparison is merged (PHA2-24). Machine-learning models, prediction
intervals and censored-demand handling inside the models are planned (PHA2-27
and later).

## Problem statement

Healthcare organizations need to know in advance which medicines are likely to
run out. The forecasting module answers one question: *how much of each medicine
will be consumed over the next N weeks?* Combined with the current stock and
expected deliveries, this forecast is turned into a shortage risk indicator by
the backend.

Key properties of the data that shape the approach:

- Consumption is often **intermittent**: many items have long runs of zero
  demand followed by occasional spikes.
- **Zero consumption and stock-out are different events.** A zero caused by an
  empty shelf is not a zero in demand and must not be learned as such.
- Items differ strongly in volume, units of measurement and seasonality, so a
  single global model is not assumed to fit all groups.
- Historical records may contain gaps, duplicates and inconsistent units.

## Input data

The module works on the data entities of [docs/requirements.md](../docs/requirements.md)
(section 5.5) and [docs/data/data-specification.md](../docs/data/data-specification.md);
the import file formats are `consumption.csv`, `stock.csv`, `receipts.csv` and
`planned_receipts.csv`, with `period_start` as the Monday of the ISO week.

| Entity | Description | Role in the module |
|---|---|---|
| Consumption (`consumption_record`) | Quantity of each item dispensed per week: `item_code`, `period_start`, `quantity` | Target series of every model |
| Stock levels (`stock_snapshot`) | Closing balance per item and week; `is_stock_out` flags weeks with an empty shelf | Censored-demand flags (FR-17) |
| Receipts (`receipt`) and planned receipts (`planned_receipt`) | Deliveries received and expected per item | Risk calculation in the backend; planned as model features |
| Lead time (`item_supplier.lead_time_days`) | Expected delivery time per supplier and item | Risk calculation in the backend (FR-08) |

No patient-level or personal data is used anywhere in the pipeline (NFR-04).

Decisions recorded during requirements analysis (initial, to be confirmed on real data):

- Forecast horizon and time step: **weekly step, 12-week horizon**, configurable per run (see [docs/proposal.md](../docs/proposal.md) and [docs/requirements.md](../docs/requirements.md), FR-06)
- List of medicines or medicine groups in scope: **all active catalogue items**; evaluation is reported per medicine group and separately for rarely consumed items (see [docs/verification-and-evaluation-plan.md](../docs/verification-and-evaluation-plan.md))
- Data source and conditions of use: **access to a healthcare organization's history requested, answer pending** (task PHA2-26); a documented synthetic dataset is used for development meanwhile (see [docs/data/data-specification.md](../docs/data/data-specification.md) and [data/README.md](data/README.md))

## Data preparation

The preparation stage produces a clean, regular weekly series per item:

1. **Validation** (`forecasting.data.validation`, implemented): required columns,
   types, duplicate item-week pairs, negative or missing quantities, dates that
   are not Mondays. Malformed input raises `DataValidationError` with a list of
   problems instead of producing a forecast (NFR-06).
2. **Regular weekly series** (`make_regular_weekly`, implemented): weeks missing
   between an item's first week and the last week of the frame are filled with
   zero consumption and flagged `is_filled`, so that gaps are visible and
   counted rather than silently ignored.
3. **Stock-out detection** (flagging implemented, model handling planned): weeks
   in which the closing stock was zero are flagged `is_stock_out`, so that zero
   consumption in these weeks is treated as censored demand, not as true zero
   demand (FR-17). The experiment runner already excludes such weeks from
   training and from the metrics; handling inside `forecast_items` is planned.
4. **Outlier handling** (planned) with rules that are documented and applied
   identically to training and evaluation data.
5. **Feature engineering** (planned, PHA2-27): calendar features, lagged
   consumption, rolling statistics, item group attributes. All features are
   computed using only past observations relative to the forecast origin.

## Models

Two families are compared on identical data and time windows.

**Baselines** (`forecasting/forecasting/models/baselines.py`, implemented) are
the reference points that every model must beat. Their names are the shared
vocabulary used in configurations, in the API contract and in the experiment
runner:

| Name | Method | Parameters |
|---|---|---|
| `naive` | Last observed value | — |
| `seasonal_naive` | Value of the same week one season earlier; falls back to `naive` when the history is shorter than one season | `season_length` (default 52) |
| `moving_average` | Mean of the last `window` weeks | `window` (default 8) |
| `croston` | Croston's method for intermittent demand: separate exponential smoothing of demand sizes and demand intervals | `alpha` (default 0.1) |
| `sba` | Syntetos–Boylan approximation: Croston's forecast corrected by the factor 1 − α/2 | `alpha` (default 0.1) |

**Machine learning models** (planned, PHA2-27; LightGBM is the first candidate,
see [docs/technology-comparison.md](../docs/technology-comparison.md);
statsforecast and LightGBM enter the dependencies with the candidate models):

- Gradient boosting on lag and calendar features
- Global models trained across items with item-level identifiers

Model selection and hyperparameter tuning are done on the validation period
only. The test period is used once, for the final comparison.

## Evaluation

- **Time-based split** (`forecasting/forecasting/evaluation/split.py`,
  implemented): `split_by_cutoff` divides observations into train, validation
  and test parts by calendar cut-off dates; `rolling_origin_windows` enumerates
  several forecast origins over a regular weekly series and returns `Window`
  objects with half-open `train`, `validation` and `test` index ranges. Nothing
  is shuffled, and no future observation is used when fitting or selecting
  models.
- **Metrics** (`forecasting/forecasting/evaluation/metrics.py`, implemented):
  `mae`, `wape` and `bias`. `wape` returns `None` when the total actual
  consumption in the window is zero (FR-16).
- **Error analysis** is reported per medicine group and per demand class
  (smooth, intermittent, erratic, lumpy), where standard metrics are least
  informative for rarely consumed items.
- **Shortage scenarios** (planned): with fixed delivery assumptions, forecasts
  are converted to shortage risk and compared with actual stock-out events;
  precision and recall of the alerts are the measures
  ([docs/verification-and-evaluation-plan.md](../docs/verification-and-evaluation-plan.md)).

## Reproducibility

Every experiment must be reproducible from a clean checkout (NFR-05):

- Fixed random seeds for all stochastic components (the baselines are
  deterministic; the seed is recorded with every run).
- Dependency versions declared in `pyproject.toml`; the versions used are
  recorded in the results.
- Experiment configuration (dataset identifier, split, horizon, models and
  parameters, seed) stored as a YAML file under `experiments/configs/` and
  copied next to the results.
- One entry point per experiment type (`experiments/run_baselines.py` for the
  baseline comparison); results (metrics, predictions) are written per run and
  are not committed (see [experiments/README.md](experiments/README.md)).

Robustness requirement (NFR-06): the module fails with a clear error, not a
wrong forecast, when it receives malformed input (missing columns, wrong types,
negative quantities, dates that are not Mondays, duplicate weeks).

## Interface with the backend

The backend calls the module in-process; there is no HTTP between them. The
contract is defined in [docs/architecture/api-contract.md](../docs/architecture/api-contract.md),
section 5, and implemented in `forecasting/forecasting/api.py`:

```python
from forecasting.api import ForecastConfig, ForecastResult, forecast_items

result = forecast_items(history, horizon, config)   # -> ForecastResult
```

- **Input**: `history`, a pandas frame with one row per item and week
  (`item_code`, `period_start`, `quantity`; optional `is_stock_out`,
  `item_name`, `unit`); `horizon`, the number of weeks to forecast (1–52,
  default 12); `config`, a `ForecastConfig(model, horizon, params)` or a mapping
  with the same keys, where `model` is one of the baseline names above.
- **Output**: `ForecastResult` with `forecasts` (`item_code`, `period_start`,
  `point`, `model`; one row per item and forecast week), `item_info` (history
  length, filled and censored weeks and the model used per item),
  `model_name`, `horizon`, `origin`, `config` and `warnings`.
- **Errors**: malformed input raises `DataValidationError` before any model is
  fitted; an invalid configuration raises `ValueError` (NFR-06).

Prediction intervals (`lower`, `upper`), the fallback model for short
histories, a random seed for stochastic models and censoring handling inside
the models are planned extensions of the same interface (API contract,
section 5.8).

## Directory layout

```
forecasting/
├── forecasting/                 # importable package (pip install -e forecasting)
│   ├── data/                    # schema.py (column names, constants), validation.py
│   ├── models/                  # baselines.py: naive, seasonal_naive, moving_average, croston, sba
│   ├── evaluation/              # metrics.py: mae, wape, bias; split.py: split_by_cutoff, rolling_origin_windows
│   └── api.py                   # forecast_items(history, horizon, config) -> ForecastResult
├── data/                        # generate_synthetic.py, sample/ (committed synthetic sample), README.md
├── experiments/                 # configs/, run_baselines.py, results/ (runs not committed), README.md (PHA2-24)
├── tests/                       # pytest: test_validation, test_baselines, test_metrics, test_split, test_api
├── pyproject.toml               # dependencies, "dev" extra, pytest configuration
└── README.md                    # this file
```

Machine-learning models and feature preparation are added under
`forecasting/forecasting/models/` and `forecasting/forecasting/features/` with
PHA2-27. Raw and processed datasets are never committed (see the root
`.gitignore`); only the small documented sample under `data/sample/` is tracked.

## Roadmap

| Period | Deliverable |
|---|---|
| Nov–Dec 2026 | Baseline comparison on the synthetic dataset (EXP-01), first ML model (PHA2-27), censoring experiment |
| Jan 2027 | Forecast served through the API, end-to-end demo with the web interface |
| Feb 2027 | Hyperparameter tuning, prediction intervals, refined shortage risk inputs |
| Mar 2027 | Final experiments on the test period, model comparison, error analysis |
| Apr 2027 | Technical documentation of the module, results for the thesis and paper |
