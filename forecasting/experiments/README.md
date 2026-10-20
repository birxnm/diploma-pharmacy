# Forecasting experiments

Task: PHA2-24 · Last updated: 2026-10-20 · Author: Evelina Penkova

This directory holds the experiments of the forecasting module: versioned configurations, the runner scripts and the results they produce. It implements the experiment procedure of `docs/verification-and-evaluation-plan.md` (section 4) and the reproducibility requirement NFR-05 / FQ-11: every result must be reproducible from a configuration file, a dataset identifier and one command.

## Layout

| Path | Content | Tracked in git |
|---|---|---|
| `configs/<name>.yaml` | One file per experiment: dataset, split, censoring method, models and parameters, seed | yes |
| `run_baselines.py` | Runner for the baseline comparison (FR-16): rolling-origin evaluation of the five baselines, metrics and predictions per run | yes |
| `results/<run-id>/config.yaml` | Verbatim copy of the configuration the run used | no (see `results/README.md`) |
| `results/<run-id>/metrics.json` | Metrics per model: overall, per demand class and per origin; windows, dataset summary, diagnostics | no |
| `results/<run-id>/predictions.csv` | Every point forecast of the run with the actual value | no |
| `reports/EXP-<nn>.md` | Experiment report with the summary tables copied from `metrics.json` (planned, template in the evaluation plan, section 4.10) | yes |

## Naming

- Configuration files are named after what they compare: `baselines.yaml` for the baseline comparison; later experiments follow the evaluation plan and are named `EXP-<nn>-<slug>.yaml` with a running number (`EXP-01-baselines`, `EXP-02-censoring`, ...).
- A run directory is `results/<experiment>-<YYYYMMDD-HHMMSS>` by default (`experiment` is the key of the same name in the configuration, the timestamp is UTC). A directory name can be chosen with `--out` for local work, for example `results/baselines-local`.
- Dataset identifiers follow the evaluation plan (section 4.2): the committed sample is `synthetic-0.1.0-i20-w104-s42` (generator version, items, weeks, seed). Real data, once available, stay outside the repository and are referenced by identifier only.

## Running the baseline comparison

From the repository root, with the forecasting package importable (`pip install -e forecasting`, or `PYTHONPATH=forecasting` for a one-off run):

```
python forecasting/experiments/run_baselines.py \
    --config forecasting/experiments/configs/baselines.yaml \
    --out forecasting/experiments/results/baselines-local
```

Both arguments are optional: `--config` defaults to `configs/baselines.yaml`, `--out` to `results/<experiment>-<timestamp>`. Relative paths inside the configuration (`dataset.path`) are resolved from the repository root, so the command works from any working directory. The runner refuses to write into a directory that already holds a `metrics.json`.

What the run does, in order:

1. Loads and validates the configuration. Unknown models, a missing baseline (when `require_all_baselines` is true, FR-16 scenario S4) or an unimplemented `censoring_method` stop the run.
2. Reads `consumption.csv` and `stock.csv` from `dataset.path`, validates them with `forecasting.data.validation` (FR-02, NFR-06) and builds a contiguous weekly series per item with `make_regular_weekly`: weeks without a record are zero consumption (FQ-02).
3. Marks stock-out weeks: a week is a stock-out week when `quantity_on_hand` in `stock.csv` is zero (`docs/data/data-specification.md`, section 7; weeks without a stock row are never flagged). Recorded consumption in such a week is censored demand (FR-17, FQ-10). With `censoring_method: exclude` these weeks are removed from the training series and excluded from the metrics; they are still listed in `predictions.csv` with `is_censored = true` and an empty `actual`.
4. Places the evaluation windows with `forecasting.evaluation.split.rolling_origin_windows(n_periods, horizon, n_windows, min_train)` (FQ-09). The function returns a list of `Window(origin, horizon, validation_length)` objects whose `train`, `validation` and `test` properties are half-open index ranges (end indices exclusive); the runner uses no validation part, so the training range ends at the origin. It derives `(train_end, test_start, test_end)` from `train.stop`, `test.start` and `test.stop`, checks each window against the number of weeks, `min_train_weeks` and the horizon, and writes the resulting origin dates to `metrics.json`. A comparison is only valid between runs that report the same origins (evaluation plan, section 4.4).
5. At every origin and for every item, drops the censored weeks from the history before the origin, classifies the item by demand class on that history (Syntetos–Boylan scheme with the cut-offs of the synthetic generator: ADI 1.32, CV² 0.49; `insufficient` when fewer than two non-zero weeks), fits every configured baseline with `fit(history)` and takes `predict(h)` for the test weeks. Items with fewer than `min_history_weeks` non-censored training weeks are skipped at that origin and listed (FQ-04); items whose whole test window is censored are listed as well.
6. Computes `mae`, `wape` and `bias` from `forecasting.evaluation.metrics` on the non-censored test weeks, pooled over items and weeks (FQ-08): per model overall, per demand class and per origin. WAPE is `null` when the actual consumption in the pooled set is zero.
7. Writes `config.yaml`, `metrics.json` and `predictions.csv` and prints a summary table.

## Configuration format

`configs/baselines.yaml` is the reference. Keys:

| Key | Meaning |
|---|---|
| `experiment`, `task` | Name used in the run directory and `metrics.json`; Linear issue of the experiment |
| `dataset.id`, `dataset.path` | Dataset identifier and directory with `consumption.csv` and `stock.csv` (and `dataset.json` for synthetic sets, copied into `metrics.json`) |
| `split.horizon_weeks` | Length of every test window (default horizon 12, FQ-03) |
| `split.n_windows` | Number of rolling origins (at least three in the plan) |
| `split.min_train_weeks` | Shortest training history at any origin; 52 keeps `seasonal_naive` applicable |
| `censoring_method` | `exclude` (implemented); `impute` is planned (FQ-10, open question Q8 of the requirements) |
| `min_history_weeks` | Minimum non-censored training weeks per item and origin (default 12, FQ-04) |
| `require_all_baselines` | Refuse a configuration that omits one of the five baselines (default true) |
| `seed` | Recorded with the results; the baselines are deterministic, the seed is passed to the machine-learning models of later experiments |
| `models` | List of `{name, params}`; names `naive`, `seasonal_naive`, `moving_average`, `croston`, `sba`; `params` are the constructor arguments of the forecaster class |

## Result files

`metrics.json`:

| Block | Content |
|---|---|
| `experiment`, `task`, `run_id` | Identification of the run |
| `run` | Configuration file, start and end time (UTC), versions of the forecasting package, pandas and numpy |
| `dataset` | Identifier, path, number of items and weeks, first and last week, number of stock-out weeks, generator manifest when present |
| `split` | Horizon, number of windows, minimum training length and, per window, origin, training and test week ranges |
| `censoring_method`, `min_history_weeks`, `seed` | Copied from the configuration |
| `evaluation` | Test weeks and censored test weeks per model, items skipped for insufficient history (per origin), items with a fully censored test window |
| `models.<name>` | `params`; `fallback_fits` (number of item-origin fits in which the forecaster fell back to a simpler forecast, for example `seasonal_naive` to naive when the history is shorter than one season); `overall`, `by_demand_class.<class>` and `by_origin[]`, each with `mae`, `wape`, `bias`, `n_weeks` (scored), `censored_weeks`, `n_items` |
| `ranking` | Model names ordered by overall MAE and by overall WAPE |

`predictions.csv` has one row per model, origin, item and test week:

| Column | Content |
|---|---|
| `model` | Model name |
| `origin` | Monday of the first test week of the window (ISO date) |
| `item_code` | Item |
| `demand_class` | Class of the item on the training window at this origin |
| `period_start` | Test week (ISO date) |
| `horizon_step` | 1 ... `horizon_weeks` |
| `actual` | Recorded consumption; empty when the week is censored or not available |
| `is_censored` | `True` when the week is excluded from the metrics |
| `point` | Point forecast |

Prediction intervals (`lower`, `upper`, FQ-07) and metrics per medicine group and per horizon step are planned together with the forecasting API and the candidate models; the `metrics_*.csv` and `metadata.json` files of the evaluation plan (section 4.9) will be added when the first candidate model is compared (task PHA2-27).

## Reproducibility rules

1. A run is defined by its configuration file; nothing is passed on the command line except the file and the output directory. Changing a parameter means changing (or copying) the configuration file.
2. The configuration carries the dataset identifier and a fixed `seed`. The runner copies the configuration into the run directory and records package versions and the windows actually used.
3. Determinism check (NFR-05 scenario S1): run the same configuration twice into two directories; `predictions.csv` must be byte-identical and `metrics.json` must differ only in `run_id` and the `run` block. A difference is a defect, not a result.
4. Results are produced locally and are not committed as run directories; the tables that enter a report are copied from `metrics.json` into `reports/EXP-<nn>.md` together with the run id and the configuration name (see `results/README.md`).
5. Every result on the synthetic dataset is reported as a result on synthetic data; rankings obtained on it are checked again on real data when available (evaluation plan, section 4.2).

## Status

| Item | Status |
|---|---|
| Layout, baseline configuration, runner with rolling-origin evaluation, censoring by exclusion, demand classes, `metrics.json` and `predictions.csv` | done (this task) |
| Run of `configs/baselines.yaml` on the committed sample and first results table in a report | planned (PHA2-27 prepares the report together with the first candidate model) |
| Imputation of censored weeks, prediction intervals, metrics per medicine group and per horizon step, alert replay (FQ-15) | planned |
| Generic entry point `python -m forecasting.experiments.run <config>` for candidate models (evaluation plan, section 4.9) | planned; `run_baselines.py` stays the reference for the baseline comparison |
