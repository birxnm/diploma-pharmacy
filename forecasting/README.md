# Forecasting Module

This directory contains the data preparation pipeline and the demand forecasting
models of the smart supply chain analytics system for pharmaceutical inventory.
The module predicts medicine consumption per item over a fixed horizon and
provides the forecasts that the backend uses to calculate shortage risk.

**Owner:** Evelina Penkova (data preparation, forecasting models, experiments)

## Problem statement

Healthcare organizations need to know in advance which medicines are likely to
run out. The forecasting module answers one question: *how much of each medicine
will be consumed over the next N periods?* Combined with the current stock and
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

The module works with the following entities (exact schema is agreed with the
backend):

| Entity | Description |
|---|---|
| Consumption | Quantity of each medicine dispensed per period |
| Stock levels | Quantity on hand at the end of each period |
| Receipts | Incoming deliveries per period |
| Lead time (optional) | Expected delivery time per supplier or item |
| Expiry (optional) | Shelf-life information per batch |

No patient-level or personal data is used anywhere in the pipeline.

Open questions to be fixed during requirements analysis:

- Forecast horizon and time step: **TBD**
- List of medicines or medicine groups in scope: **TBD**
- Data source and conditions of use: **TBD** (must be confirmed before experiments start)

## Data preparation

The preparation stage produces a clean, regular time series per item and
includes:

1. **Validation** of raw records: types, units, duplicates, negative quantities.
2. **Resampling** to the agreed time step with explicit handling of missing periods.
3. **Stock-out detection**: periods where stock was zero are flagged so that
   zero consumption in these periods is treated as censored demand, not as true
   zero demand.
4. **Outlier handling** with rules that are documented and applied identically
   to training and evaluation data.
5. **Feature engineering**: calendar features, lagged consumption, rolling
   statistics, item group attributes. All features are computed using only
   past observations relative to the forecast origin.

## Models

Two families are compared on identical data and time windows.

**Baselines** (reference points that every model must beat):

- Naive (last value)
- Seasonal naive
- Moving average / simple exponential smoothing
- Methods designed for intermittent demand (e.g. Croston-type)

**Machine learning models** (candidates, final choice TBD):

- Gradient boosting on lag and calendar features
- Global models trained across items with item-level identifiers

Model selection and hyperparameter tuning are done on the validation period
only. The test period is used once, for the final comparison.

## Evaluation

- **Time-based split**: train → validation → test in chronological order. No
  future observations are used when building features or selecting models.
- **Metrics**: MAE and WAPE. WAPE is reported only where total actual
  consumption in the window is greater than zero.
- **Error analysis** is reported per medicine group and separately for rarely
  consumed items, where standard metrics are least informative.
- **Shortage scenarios**: with fixed delivery assumptions, forecasts are
  converted to shortage risk and compared with actual stock-out events.

## Reproducibility

Every experiment must be reproducible from a clean checkout:

- Fixed random seeds for all stochastic components.
- Pinned dependency versions.
- Experiment configuration (data window, horizon, features, model parameters)
  stored as a file next to the results.
- A single entry point to run data preparation, training and evaluation.
- Results (metrics, plots, predictions on the test period) saved per run.

Robustness requirement: the module must fail with a clear error, not a wrong
forecast, when it receives malformed input (missing columns, wrong units,
non-monotonic dates).

## Interface with the backend

The forecasting module is exposed to the backend through the project API
(implemented together with the backend part). The contract is:

- **Input**: item identifiers, historical consumption and stock series, forecast
  horizon.
- **Output**: per-item forecast for each period of the horizon, together with
  the model version used and basic quality indicators from validation.

The exact request and response formats are documented in the API docs once agreed.

## Directory layout

```
forecasting/
├── data/          # raw and processed data (not committed), data loading code
├── notebooks/     # exploratory analysis and error analysis
├── features/      # feature engineering
├── models/        # baselines and ML models
├── experiments/   # configs and saved results per run
├── evaluation/    # metrics, splits, reports
└── README.md
```

## Roadmap

| Period | Deliverable |
|---|---|
| Nov–Dec 2026 | Data validation and preparation pipeline, baseline forecasts, first ML models |
| Jan 2027 | Forecast served through the API, end-to-end demo with the web interface |
| Feb 2027 | Hyperparameter tuning, refined shortage risk inputs |
| Mar 2027 | Final experiments on the test period, model comparison, error analysis |
| Apr 2027 | Technical documentation of the module, results for the thesis and paper |
