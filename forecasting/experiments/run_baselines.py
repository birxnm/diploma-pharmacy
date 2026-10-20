"""Baseline evaluation runner of the PharmaStock forecasting package (PHA2-24).

The script reads a YAML experiment configuration, loads ``consumption.csv``
and ``stock.csv`` from the configured dataset directory, builds a regular
weekly series per item, evaluates every configured baseline on rolling-origin
windows and writes one results directory containing ``config.yaml`` (copy of
the configuration), ``metrics.json`` and ``predictions.csv``. The layout and
the reproducibility rules are described in ``forecasting/experiments/README.md``.

Usage, from the repository root with the ``forecasting`` package importable
(``pip install -e forecasting`` or ``PYTHONPATH=forecasting``)::

    python forecasting/experiments/run_baselines.py \
        --config forecasting/experiments/configs/baselines.yaml \
        --out forecasting/experiments/results/baselines-local

Weeks in which an item was out of stock are censored demand (FR-17, FQ-10):
they are removed from the training series and excluded from the metrics. A
malformed configuration or dataset stops the run with an error before any
result is written (NFR-06).
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import forecasting
from forecasting.data.schema import (
    IS_STOCK_OUT,
    ITEM_CODE,
    PERIOD_START,
    QUANTITY,
    QUANTITY_ON_HAND,
    WEEKLY_FREQ,
)
from forecasting.data.validation import make_regular_weekly, validate_consumption, validate_stock
from forecasting.evaluation.metrics import bias, mae, wape
from forecasting.evaluation.split import rolling_origin_windows
from forecasting.models.baselines import (
    CrostonForecaster,
    MovingAverageForecaster,
    NaiveForecaster,
    SBAForecaster,
    SeasonalNaiveForecaster,
)

EXPERIMENTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENTS_DIR.parents[1]
DEFAULT_CONFIG = EXPERIMENTS_DIR / "configs" / "baselines.yaml"
DEFAULT_RESULTS_DIR = EXPERIMENTS_DIR / "results"

CONSUMPTION_FILE = "consumption.csv"
STOCK_FILE = "stock.csv"
MANIFEST_FILE = "dataset.json"

# Baselines of FQ-05 by their configuration name.
BASELINES = {
    "naive": NaiveForecaster,
    "seasonal_naive": SeasonalNaiveForecaster,
    "moving_average": MovingAverageForecaster,
    "croston": CrostonForecaster,
    "sba": SBAForecaster,
}

# Syntetos–Boylan demand classification, with the cut-offs and the formulas
# of forecasting/data/generate_synthetic.py (docs/data/data-specification.md).
ADI_CUTOFF = 1.32
CV2_CUTOFF = 0.49
DEMAND_CLASSES = ("smooth", "intermittent", "erratic", "lumpy", "insufficient")

CENSORING_METHODS = ("exclude",)
DATE_FORMAT = "%Y-%m-%d"
PREDICTION_COLUMNS = [
    "model",
    "origin",
    "item_code",
    "demand_class",
    "period_start",
    "horizon_step",
    "actual",
    "is_censored",
    "point",
]


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


def _require(mapping, key, kind, where, minimum=None):
    """Return ``mapping[key]`` checked for type (and lower bound), or raise ``ValueError``."""
    if not isinstance(mapping, dict) or key not in mapping:
        raise ValueError(f"configuration: '{where}' must define '{key}'")
    value = mapping[key]
    wrong_bool = isinstance(value, bool) and kind is not bool
    if wrong_bool or not isinstance(value, kind):
        raise ValueError(f"configuration: '{where}.{key}' must be of type {kind.__name__}, got {value!r}")
    if minimum is not None and value < minimum:
        raise ValueError(f"configuration: '{where}.{key}' must be at least {minimum}, got {value!r}")
    return value


def load_config(path):
    """Read and validate the experiment configuration; return it as a dict."""
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"{path}: the configuration must be a mapping")

    _require(config, "experiment", str, "root")
    dataset = _require(config, "dataset", dict, "root")
    _require(dataset, "path", str, "dataset")
    split = _require(config, "split", dict, "root")
    _require(split, "horizon_weeks", int, "split", minimum=1)
    _require(split, "n_windows", int, "split", minimum=1)
    _require(split, "min_train_weeks", int, "split", minimum=1)
    _require(config, "seed", int, "root")
    config.setdefault("censoring_method", "exclude")
    if config["censoring_method"] not in CENSORING_METHODS:
        raise ValueError(
            f"configuration: censoring_method {config['censoring_method']!r} is not implemented; "
            f"expected one of {', '.join(CENSORING_METHODS)}"
        )
    config.setdefault("min_history_weeks", 12)
    _require(config, "min_history_weeks", int, "root", minimum=1)
    config.setdefault("require_all_baselines", True)
    _require(config, "require_all_baselines", bool, "root")

    models = _require(config, "models", list, "root")
    if not models:
        raise ValueError("configuration: 'models' must list at least one model")
    names = []
    for position, entry in enumerate(models):
        name = _require(entry, "name", str, f"models[{position}]")
        if name not in BASELINES:
            raise ValueError(
                f"configuration: unknown model {name!r}; expected one of {', '.join(BASELINES)}"
            )
        if name in names:
            raise ValueError(f"configuration: model {name!r} is listed twice")
        names.append(name)
        params = entry.setdefault("params", {})
        if params is None:
            entry["params"] = {}
        elif not isinstance(params, dict):
            raise ValueError(f"configuration: 'models[{position}].params' must be a mapping")
    missing = [name for name in BASELINES if name not in names]
    if missing and config["require_all_baselines"]:
        raise ValueError(
            "configuration: a baseline comparison must include every baseline (FR-16); "
            f"missing: {', '.join(missing)}. Set require_all_baselines: false for a partial run."
        )
    return config


def resolve_path(value):
    """Resolve a configuration path: absolute as is, relative from the repository root."""
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def display_path(path):
    """Path as written into the results: relative to the repository root when inside it."""
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------


def load_weekly_panel(data_dir):
    """Return ``(quantity, censored)`` frames indexed by week with one column per item.

    ``quantity`` holds the recorded weekly consumption (NaN before an item's
    first week); ``censored`` is True in weeks in which the item was out of
    stock, derived from ``stock.csv`` as a closing balance of zero. Both files
    go through the package validation first, so malformed input stops the run
    with a structured error (NFR-06).
    """
    for name in (CONSUMPTION_FILE, STOCK_FILE):
        if not (data_dir / name).is_file():
            raise FileNotFoundError(f"dataset file not found: {data_dir / name}")
    consumption = validate_consumption(pd.read_csv(data_dir / CONSUMPTION_FILE))
    stock = validate_stock(pd.read_csv(data_dir / STOCK_FILE))

    stock_out = stock[[ITEM_CODE, PERIOD_START]].copy()
    stock_out["stock_out_from_stock"] = (stock[QUANTITY_ON_HAND] <= 0).to_numpy(dtype=bool)
    merged = consumption.merge(stock_out, how="left", on=[ITEM_CODE, PERIOD_START])
    flags = merged["stock_out_from_stock"].fillna(False).astype(bool)
    if IS_STOCK_OUT in merged.columns:
        flags = flags | merged[IS_STOCK_OUT].fillna(False).astype(bool)
    merged[IS_STOCK_OUT] = flags.to_numpy(dtype=bool)
    merged = merged.drop(columns=["stock_out_from_stock"])

    regular = make_regular_weekly(merged)
    index = pd.date_range(regular[PERIOD_START].min(), regular[PERIOD_START].max(), freq=WEEKLY_FREQ)
    quantity = regular.pivot(index=PERIOD_START, columns=ITEM_CODE, values=QUANTITY).reindex(index)
    censored = (
        regular.pivot(index=PERIOD_START, columns=ITEM_CODE, values=IS_STOCK_OUT)
        .reindex(index)
        .fillna(False)
        .astype(bool)
    )
    return quantity.astype(float), censored


def read_manifest(data_dir):
    """Return the generator manifest of a synthetic dataset, or None when absent."""
    path = data_dir / MANIFEST_FILE
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    keys = ("dataset", "generator", "generator_version", "parameters", "period")
    return {key: manifest[key] for key in keys if key in manifest}


def classify_demand(values):
    """Syntetos–Boylan class of a series of non-censored weekly quantities."""
    nonzero = values[values > 0]
    if nonzero.size < 2:
        return "insufficient"
    adi = values.size / nonzero.size
    mean = float(nonzero.mean())
    cv2 = float(nonzero.var(ddof=1)) / (mean * mean)
    if adi < ADI_CUTOFF:
        return "smooth" if cv2 < CV2_CUTOFF else "erratic"
    return "intermittent" if cv2 < CV2_CUTOFF else "lumpy"


# --------------------------------------------------------------------------
# Windows
# --------------------------------------------------------------------------


def resolve_windows(n_periods, horizon, n_windows, min_train):
    """Return validated ``(train_end, test_start, test_end)`` index triples.

    The windows come from ``forecasting.evaluation.split.rolling_origin_windows``,
    which returns ``Window`` objects with half-open ``train``, ``validation``
    and ``test`` ranges; the runner uses no validation part, so ``train_end``
    is the origin. ``train_end`` and ``test_end`` are exclusive. Each window is
    checked so that an unexpected contract is reported instead of producing
    wrong metrics.
    """
    raw = rolling_origin_windows(n_periods, horizon, n_windows, min_train)
    windows = []
    for entry in raw:
        try:
            train_end, test_start, test_end = (
                int(entry.train.stop),
                int(entry.test.start),
                int(entry.test.stop),
            )
        except AttributeError:
            raise ValueError(
                f"rolling_origin_windows returned {entry!r}; expected a Window "
                "with 'train' and 'test' ranges"
            ) from None
        if not min_train <= train_end <= test_start < test_end <= n_periods:
            raise ValueError(
                f"window ({train_end}, {test_start}, {test_end}) is inconsistent with "
                f"{n_periods} periods and min_train={min_train}"
            )
        if test_end - test_start > horizon:
            raise ValueError(
                f"window ({train_end}, {test_start}, {test_end}) is longer than the horizon {horizon}"
            )
        windows.append((train_end, test_start, test_end))
    if not windows:
        raise ValueError("rolling_origin_windows returned no windows")
    if len(set(windows)) != len(windows):
        raise ValueError("rolling_origin_windows returned duplicate windows")
    return sorted(windows)


def describe_windows(index, windows):
    """Window dates for ``metrics.json``."""
    return [
        {
            "origin": index[test_start].strftime(DATE_FORMAT),
            "train_first_week": index[0].strftime(DATE_FORMAT),
            "train_last_week": index[train_end - 1].strftime(DATE_FORMAT),
            "train_weeks": int(train_end),
            "test_first_week": index[test_start].strftime(DATE_FORMAT),
            "test_last_week": index[test_end - 1].strftime(DATE_FORMAT),
            "test_weeks": int(test_end - test_start),
        }
        for train_end, test_start, test_end in windows
    ]


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------


def evaluate(config, quantity, censored, windows):
    """Fit every model at every origin for every item; return predictions and diagnostics."""
    min_history = config["min_history_weeks"]
    index = quantity.index
    records = []
    insufficient = []
    fully_censored = []
    fallbacks = {entry["name"]: 0 for entry in config["models"]}

    for train_end, test_start, test_end in windows:
        origin = index[test_start].strftime(DATE_FORMAT)
        steps = test_end - train_end
        offset = test_start - train_end
        test_weeks = [index[position].strftime(DATE_FORMAT) for position in range(test_start, test_end)]
        for item in quantity.columns:
            y = quantity[item].to_numpy(dtype=float)
            out = censored[item].to_numpy(dtype=bool)
            train = y[:train_end]
            history = train[~np.isnan(train) & ~out[:train_end]]
            if history.size < min_history:
                insufficient.append({"origin": origin, "item_code": item, "weeks": int(history.size)})
                continue
            demand_class = classify_demand(history)
            actual = y[test_start:test_end].copy()
            is_censored = out[test_start:test_end] | np.isnan(actual)
            actual[is_censored] = np.nan
            if is_censored.all():
                fully_censored.append({"origin": origin, "item_code": item})
            for entry in config["models"]:
                model = BASELINES[entry["name"]](**entry["params"]).fit(history)
                point = np.asarray(model.predict(steps), dtype=float)[offset:]
                if point.shape != actual.shape:
                    raise ValueError(
                        f"{entry['name']}: predict({steps}) returned shape {point.shape}, "
                        f"expected ({steps},)"
                    )
                if bool(getattr(model, "fallback_used_", False)):
                    fallbacks[entry["name"]] += 1
                for step in range(actual.size):
                    records.append(
                        {
                            "model": entry["name"],
                            "origin": origin,
                            "item_code": item,
                            "demand_class": demand_class,
                            "period_start": test_weeks[step],
                            "horizon_step": step + 1,
                            "actual": actual[step],
                            "is_censored": bool(is_censored[step]),
                            "point": float(point[step]),
                        }
                    )

    predictions = pd.DataFrame.from_records(records, columns=PREDICTION_COLUMNS)
    diagnostics = {
        "items_insufficient_history": insufficient,
        "items_fully_censored": fully_censored,
    }
    return predictions, diagnostics, fallbacks


def _metric_value(value):
    """Metric as a JSON number, or None (WAPE is undefined when actuals sum to zero)."""
    if value is None:
        return None
    number = float(value)
    if not np.isfinite(number):
        return None
    return round(number, 6)


def summarise(frame):
    """MAE, WAPE and bias over the non-censored rows of ``frame`` (pooled over items and weeks)."""
    scored = frame[~frame["is_censored"]]
    summary = {
        "n_weeks": int(len(scored)),
        "censored_weeks": int(len(frame) - len(scored)),
        "n_items": int(frame["item_code"].nunique()),
    }
    if scored.empty:
        summary.update({"mae": None, "wape": None, "bias": None})
        return summary
    actual = scored["actual"].to_numpy(dtype=float)
    point = scored["point"].to_numpy(dtype=float)
    summary["mae"] = _metric_value(mae(actual, point))
    summary["wape"] = _metric_value(wape(actual, point))
    summary["bias"] = _metric_value(bias(actual, point))
    return summary


def summarise_models(config, predictions, fallbacks):
    """Per model: overall, per demand class and per origin summaries."""
    result = {}
    for entry in config["models"]:
        frame = predictions[predictions["model"] == entry["name"]]
        by_class = {
            demand_class: summarise(group)
            for demand_class in DEMAND_CLASSES
            for group in [frame[frame["demand_class"] == demand_class]]
            if not group.empty
        }
        by_origin = [
            dict(origin=origin, **summarise(frame[frame["origin"] == origin]))
            for origin in sorted(frame["origin"].unique())
        ]
        result[entry["name"]] = {
            "params": entry["params"],
            "fallback_fits": int(fallbacks[entry["name"]]),
            "overall": summarise(frame),
            "by_demand_class": by_class,
            "by_origin": by_origin,
        }
    return result


def rank_models(models, metric):
    """Model names ordered by the overall value of ``metric`` (undefined values last)."""
    defined = [(name, data["overall"][metric]) for name, data in models.items()]
    return [name for name, value in sorted(defined, key=lambda pair: (pair[1] is None, pair[1]))]


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def write_results(out_dir, config_path, metrics, predictions):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.yaml").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
    predictions.to_csv(out_dir / "predictions.csv", index=False, float_format="%.6f")


def print_summary(metrics):
    print(f"Experiment {metrics['experiment']} ({metrics['task']}), run {metrics['run_id']}")
    print(
        f"Dataset {metrics['dataset']['id']}: {metrics['dataset']['items']} items, "
        f"{metrics['dataset']['weeks']} weeks ({metrics['dataset']['first_week']} to "
        f"{metrics['dataset']['last_week']}), {metrics['dataset']['stock_out_weeks']} stock-out weeks"
    )
    print("Origins: " + ", ".join(window["origin"] for window in metrics["split"]["windows"]))
    print(f"{'model':<16}{'MAE':>12}{'WAPE':>10}{'bias':>12}{'weeks':>8}")
    for name, data in metrics["models"].items():
        overall = data["overall"]
        wape_text = "n/a" if overall["wape"] is None else f"{overall['wape']:.3f}"
        mae_text = "n/a" if overall["mae"] is None else f"{overall['mae']:.3f}"
        bias_text = "n/a" if overall["bias"] is None else f"{overall['bias']:+.3f}"
        print(f"{name:<16}{mae_text:>12}{wape_text:>10}{bias_text:>12}{overall['n_weeks']:>8}")


def run(config_path, out_dir):
    started = pd.Timestamp.now(tz="UTC")
    config = load_config(config_path)
    data_dir = resolve_path(config["dataset"]["path"])
    if out_dir is None:
        out_dir = DEFAULT_RESULTS_DIR / f"{config['experiment']}-{started.strftime('%Y%m%d-%H%M%S')}"
    if (out_dir / "metrics.json").exists():
        raise FileExistsError(f"{out_dir} already holds a run; choose another --out directory")

    quantity, censored = load_weekly_panel(data_dir)
    split = config["split"]
    windows = resolve_windows(
        len(quantity.index), split["horizon_weeks"], split["n_windows"], split["min_train_weeks"]
    )
    predictions, diagnostics, fallbacks = evaluate(config, quantity, censored, windows)
    if predictions.empty:
        raise ValueError("no item had enough history at any origin; nothing to evaluate")
    models = summarise_models(config, predictions, fallbacks)
    finished = pd.Timestamp.now(tz="UTC")

    metrics = {
        "experiment": config["experiment"],
        "task": config.get("task"),
        "run_id": out_dir.name,
        "run": {
            "config_file": display_path(config_path),
            "started_at": started.isoformat(timespec="seconds"),
            "finished_at": finished.isoformat(timespec="seconds"),
            "versions": {
                "forecasting": getattr(forecasting, "__version__", None),
                "pandas": pd.__version__,
                "numpy": np.__version__,
            },
        },
        "dataset": {
            "id": config["dataset"].get("id"),
            "path": display_path(data_dir),
            "items": int(quantity.shape[1]),
            "weeks": int(quantity.shape[0]),
            "first_week": quantity.index[0].strftime(DATE_FORMAT),
            "last_week": quantity.index[-1].strftime(DATE_FORMAT),
            "stock_out_weeks": int(censored.to_numpy().sum()),
            "manifest": read_manifest(data_dir),
        },
        "split": {
            "horizon_weeks": split["horizon_weeks"],
            "n_windows": split["n_windows"],
            "min_train_weeks": split["min_train_weeks"],
            "windows": describe_windows(quantity.index, windows),
        },
        "censoring_method": config["censoring_method"],
        "min_history_weeks": config["min_history_weeks"],
        "seed": config["seed"],
        "evaluation": {
            "test_weeks_per_model": int(len(predictions) // len(config["models"])),
            "censored_test_weeks_per_model": int(predictions["is_censored"].sum() // len(config["models"])),
            **diagnostics,
        },
        "models": models,
        "ranking": {"by_mae": rank_models(models, "mae"), "by_wape": rank_models(models, "wape")},
    }
    write_results(out_dir, config_path, metrics, predictions)
    print_summary(metrics)
    print(f"Results written to {out_dir}")
    return out_dir


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Evaluate the forecasting baselines on rolling-origin windows.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"experiment configuration (YAML); default: {DEFAULT_CONFIG.relative_to(REPO_ROOT)}",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="results directory; default: forecasting/experiments/results/<experiment>-<timestamp>",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    run(args.config, args.out)


if __name__ == "__main__":
    main()
