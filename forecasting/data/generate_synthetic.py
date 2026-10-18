"""Generate the PharmaStock synthetic development dataset.

Task PHA2-15. The script produces weekly pharmacy data for a fictional hospital
pharmacy in the import formats agreed in ``docs/data/data-specification.md``:

* ``consumption.csv``      item_code,item_name,unit,period_start,quantity
* ``stock.csv``            item_code,period_start,quantity_on_hand
* ``receipts.csv``         item_code,received_on,quantity,supplier
* ``planned_receipts.csv`` item_code,expected_on,quantity,supplier

Two reference files that are not import formats are written next to them:

* ``items.csv``     catalogue seed (code, name, unit, group, supplier, lead time)
* ``dataset.json``  generation parameters and per-item ground-truth labels

Optionally (``--write-truth``) the uncensored weekly demand is written to
``true_demand.csv`` for experiments on censored-demand handling.

What is modelled
----------------
* Four demand classes following the Syntetos-Boylan categorisation:
  smooth, intermittent, erratic and lumpy. Demand per week is generated as
  Bernoulli occurrence x demand size; sizes are negative-binomial (smooth),
  shifted Poisson (intermittent) or lognormal (erratic, lumpy).
* Annual multiplicative seasonality with a winter peak for some antibacterials
  and antivirals, respiratory items and antipyretics; a linear trend for a
  subset of items and a one-off demand spike (outlier) for a subset of items.
* A periodic-review order-up-to replenishment policy with per-item supplier
  and lead time. Orders become ``receipts``; orders still open at the end of
  the history become ``planned_receipts``. Deliveries of one item booked on
  the same day from the same supplier are written as one summed row, as the
  import format requires (data specification, section 3.3 and rule V-09).
* Delayed deliveries for a subset of items (a "delivery block" during which
  nothing arrives). The stock drains to zero, recorded consumption is cut to
  the stock available and is then zero while ``quantity_on_hand`` is zero.
  These weeks are the censored-demand periods that FR-17 must flag.

The output is deterministic for a given set of arguments: the same command
reproduces byte-identical files.

Usage
-----
    python forecasting/data/generate_synthetic.py --items 20 --weeks 104 \
        --seed 42 --out forecasting/data/sample
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

GENERATOR_VERSION = "0.1.0"

# Monday of the last complete week before the first pre-defense snapshot.
DEFAULT_END = "2026-10-12"
DEFAULT_ITEMS = 30
DEFAULT_WEEKS = 156
DEFAULT_SEED = 42
DEFAULT_OUT = "synthetic"

WEEKS_PER_YEAR = 52.18

# Syntetos-Boylan cut-offs used to label the observed series.
ADI_CUTOFF = 1.32
CV2_CUTOFF = 0.49

# (name, unit, group, seasonal peak ISO week or None, seasonal amplitude)
CATALOGUE: list[tuple[str, str, str, int | None, float]] = [
    ("Amoxicillin 500 mg capsules", "pack", "Antibacterials", 4, 0.35),
    ("Ceftriaxone 1 g powder for injection", "vial", "Antibacterials", 3, 0.30),
    ("Azithromycin 500 mg tablets", "pack", "Antibacterials", 5, 0.40),
    ("Ciprofloxacin 500 mg tablets", "pack", "Antibacterials", None, 0.0),
    ("Meropenem 1 g powder for injection", "vial", "Antibacterials", None, 0.0),
    ("Vancomycin 1 g powder for injection", "vial", "Antibacterials", None, 0.0),
    ("Paracetamol 500 mg tablets", "pack", "Analgesics and antipyretics", 3, 0.30),
    ("Ibuprofen 400 mg tablets", "pack", "Analgesics and antipyretics", 4, 0.20),
    ("Ketorolac 30 mg/ml solution for injection", "ampoule", "Analgesics and antipyretics", None, 0.0),
    ("Tramadol 50 mg capsules", "pack", "Analgesics and antipyretics", None, 0.0),
    ("Metformin 850 mg tablets", "pack", "Antidiabetics", None, 0.0),
    ("Insulin glargine 100 IU/ml 3 ml", "cartridge", "Antidiabetics", None, 0.0),
    ("Enoxaparin sodium 40 mg/0.4 ml", "syringe", "Anticoagulants", None, 0.0),
    ("Heparin sodium 5000 IU/ml 5 ml", "vial", "Anticoagulants", None, 0.0),
    ("Sodium chloride 0.9% 500 ml", "bottle", "Infusion solutions", None, 0.0),
    ("Glucose 5% 500 ml", "bottle", "Infusion solutions", None, 0.0),
    ("Ringer's solution 500 ml", "bottle", "Infusion solutions", None, 0.0),
    ("Omeprazole 20 mg capsules", "pack", "Gastrointestinal", None, 0.0),
    ("Ondansetron 4 mg/2 ml solution for injection", "ampoule", "Gastrointestinal", None, 0.0),
    ("Metoclopramide 10 mg/2 ml solution for injection", "ampoule", "Gastrointestinal", None, 0.0),
    ("Amlodipine 5 mg tablets", "pack", "Cardiovascular", None, 0.0),
    ("Bisoprolol 5 mg tablets", "pack", "Cardiovascular", None, 0.0),
    ("Furosemide 40 mg tablets", "pack", "Cardiovascular", None, 0.0),
    ("Losartan 50 mg tablets", "pack", "Cardiovascular", None, 0.0),
    ("Dexamethasone 4 mg/ml solution for injection", "ampoule", "Corticosteroids", None, 0.0),
    ("Propofol 10 mg/ml 20 ml emulsion", "ampoule", "Anaesthetics", None, 0.0),
    ("Lidocaine 2% 2 ml solution for injection", "ampoule", "Anaesthetics", None, 0.0),
    ("Salbutamol 100 mcg/dose inhaler", "inhaler", "Respiratory", 2, 0.35),
    ("Budesonide 0.5 mg/ml nebuliser suspension", "ampoule", "Respiratory", 2, 0.40),
    ("Oseltamivir 75 mg capsules", "pack", "Antivirals", 2, 0.60),
    ("Aciclovir 200 mg tablets", "pack", "Antivirals", None, 0.0),
    ("Fluconazole 150 mg capsules", "pack", "Antifungals", None, 0.0),
    ("Ascorbic acid 5% 2 ml solution for injection", "ampoule", "Vitamins", None, 0.0),
    ("Thiamine 5% 1 ml solution for injection", "ampoule", "Vitamins", None, 0.0),
    ("Atropine sulfate 0.1% 1 ml solution for injection", "ampoule", "Emergency medicines", None, 0.0),
    ("Epinephrine 1 mg/ml 1 ml solution for injection", "ampoule", "Emergency medicines", None, 0.0),
    ("Clopidogrel 75 mg tablets", "pack", "Anticoagulants", None, 0.0),
    ("Acetylsalicylic acid 100 mg tablets", "pack", "Cardiovascular", None, 0.0),
    ("Ceftazidime 1 g powder for injection", "vial", "Antibacterials", 3, 0.25),
    ("Ethanol 70% 100 ml solution", "bottle", "Antiseptics", None, 0.0),
]

# Longest delayed-delivery episode (weeks without any delivery).
MAX_BLOCK_WEEKS = 20

DEMAND_CLASSES = ("smooth", "intermittent", "erratic", "lumpy")
CLASS_WEIGHTS = (0.30, 0.30, 0.15, 0.25)

CENTRAL_SUPPLIER = "SK-Pharmacy"
OWN_SUPPLIERS = ("Distributor A", "Distributor B")


@dataclass
class ItemSpec:
    """Generation parameters of one item (the ground truth of the dataset)."""

    code: str
    name: str
    unit: str
    group: str
    supplier: str
    lead_time_weeks: int
    demand_class: str
    mean_weekly_demand: float
    occurrence_probability: float
    size_sigma: float
    size_dispersion: float
    seasonal_peak_week: int | None
    seasonal_amplitude: float
    trend_slope: float
    safety_weeks: int
    order_cycle_weeks: int
    # [start_week_index, target_stock_out_weeks] per delayed-delivery episode
    delivery_blocks: list[list[int]] = field(default_factory=list)
    spike_weeks: list[int] = field(default_factory=list)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the PharmaStock synthetic development dataset.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--items", type=int, default=DEFAULT_ITEMS, help="number of medicine items")
    parser.add_argument("--weeks", type=int, default=DEFAULT_WEEKS, help="number of weekly periods")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="random seed")
    parser.add_argument("--out", type=Path, default=Path(DEFAULT_OUT), help="output directory")
    parser.add_argument(
        "--end",
        type=str,
        default=DEFAULT_END,
        help="period_start (a Monday, ISO date) of the last week in the history",
    )
    parser.add_argument(
        "--write-truth",
        action="store_true",
        help="also write true_demand.csv with the uncensored weekly demand",
    )
    parser.add_argument(
        "--omit-zero-rows",
        action="store_true",
        help="omit zero-consumption rows from consumption.csv (movement-only export)",
    )
    return parser.parse_args(argv)


def validate_args(n_items: int, n_weeks: int, end: date) -> None:
    if n_items < 1:
        raise ValueError("--items must be at least 1")
    if n_weeks < 8:
        raise ValueError("--weeks must be at least 8")
    if end.weekday() != 0:
        raise ValueError(f"--end must be a Monday, got {end.isoformat()} ({end.strftime('%A')})")


def weekly_periods(end: date, n_weeks: int) -> list[date]:
    return [end - timedelta(days=7 * (n_weeks - 1 - i)) for i in range(n_weeks)]


def seasonal_factor(periods: list[date], peak_week: int | None, amplitude: float) -> np.ndarray:
    if peak_week is None or amplitude <= 0:
        return np.ones(len(periods))
    woy = np.array([p.isocalendar()[1] for p in periods], dtype=float)
    return 1.0 + amplitude * np.cos(2.0 * math.pi * (woy - peak_week) / WEEKS_PER_YEAR)


def build_item_specs(n_items: int, n_weeks: int, rng: np.random.Generator) -> list[ItemSpec]:
    specs: list[ItemSpec] = []
    for i in range(n_items):
        code = f"MED-{i + 1:04d}"
        if i < len(CATALOGUE):
            name, unit, group, peak_week, amplitude = CATALOGUE[i]
        else:
            name, unit, group, peak_week, amplitude = (f"Synthetic item {i + 1:04d}", "pack", "Other", None, 0.0)

        # The first four items cover every demand class; the rest are drawn.
        if i < len(DEMAND_CLASSES):
            demand_class = DEMAND_CLASSES[i]
        else:
            demand_class = str(rng.choice(DEMAND_CLASSES, p=CLASS_WEIGHTS))

        if demand_class == "smooth":
            level = float(rng.uniform(20, 300))
            p = float(rng.uniform(0.90, 1.00))
            sigma, dispersion = 0.0, float(rng.uniform(4, 12))
        elif demand_class == "intermittent":
            p = float(rng.uniform(0.15, 0.60))
            size_mean = float(rng.uniform(1.2, 6.0))
            level = p * size_mean
            sigma, dispersion = 0.0, 0.0
        elif demand_class == "erratic":
            level = float(rng.uniform(10, 100))
            p = float(rng.uniform(0.85, 1.00))
            sigma, dispersion = float(rng.uniform(0.7, 1.0)), 0.0
        else:  # lumpy
            p = float(rng.uniform(0.15, 0.60))
            size_mean = float(rng.uniform(5, 60))
            level = p * size_mean
            sigma, dispersion = float(rng.uniform(0.8, 1.2)), 0.0

        trend_slope = float(rng.uniform(-0.3, 0.4)) if rng.random() < 0.4 else 0.0

        if rng.random() < 0.6:
            supplier, lead_time = CENTRAL_SUPPLIER, int(rng.integers(4, 9))
        else:
            supplier, lead_time = str(rng.choice(OWN_SUPPLIERS)), int(rng.integers(1, 4))
        safety_weeks = int(rng.integers(1, 4))
        order_cycle_weeks = int(rng.integers(2, 5))

        spec = ItemSpec(
            code=code,
            name=name,
            unit=unit,
            group=group,
            supplier=supplier,
            lead_time_weeks=lead_time,
            demand_class=demand_class,
            mean_weekly_demand=round(level, 3),
            occurrence_probability=round(p, 3),
            size_sigma=round(sigma, 3),
            size_dispersion=round(dispersion, 3),
            seasonal_peak_week=peak_week,
            seasonal_amplitude=amplitude,
            trend_slope=round(trend_slope, 3),
            safety_weeks=safety_weeks,
            order_cycle_weeks=order_cycle_weeks,
        )

        # Delayed-delivery episodes: from `start` on, nothing is delivered until
        # the item has been out of stock for `target` weeks (or MAX_BLOCK_WEEKS).
        if rng.random() < 0.4:
            n_blocks = int(rng.integers(1, 3))
            lo, hi = int(0.2 * n_weeks), n_weeks - 6
            for _ in range(n_blocks):
                if hi <= lo:
                    continue
                start = int(rng.integers(lo, hi))
                target = int(rng.integers(1, 5))
                if all(abs(start - b[0]) >= MAX_BLOCK_WEEKS + 4 for b in spec.delivery_blocks):
                    spec.delivery_blocks.append([start, target])
            spec.delivery_blocks.sort()

        if rng.random() < 0.3:
            spec.spike_weeks.append(int(rng.integers(int(0.1 * n_weeks), int(0.9 * n_weeks))))

        specs.append(spec)
    return specs


def simulate_demand(spec: ItemSpec, periods: list[date], rng: np.random.Generator) -> np.ndarray:
    """Uncensored weekly demand in catalogue units (non-negative integers)."""
    n = len(periods)
    t = np.arange(n, dtype=float)
    f_season = seasonal_factor(periods, spec.seasonal_peak_week, spec.seasonal_amplitude)
    f_trend = 1.0 + spec.trend_slope * t / max(n - 1, 1)
    factor = np.clip(f_season * f_trend, 0.05, None)

    p = spec.occurrence_probability
    m = spec.mean_weekly_demand
    demand = np.zeros(n, dtype=np.int64)

    if spec.demand_class in ("smooth", "erratic"):
        # seasonality and trend act on the demand size, occurrence is constant
        occurs = rng.random(n) < p
        size_mean = (m / p) * factor
        if spec.demand_class == "smooth":
            k = spec.size_dispersion
            rates = rng.gamma(k, size_mean / k)
            sizes = rng.poisson(rates)
        else:
            sigma = spec.size_sigma
            sizes = np.rint(rng.lognormal(np.log(size_mean) - sigma**2 / 2.0, sigma)).astype(np.int64)
        sizes = np.maximum(sizes, 1)
        demand[occurs] = sizes[occurs]
    else:
        # seasonality and trend act on the occurrence probability, size is constant
        p_t = np.clip(p * factor, 0.02, 0.95)
        occurs = rng.random(n) < p_t
        size_mean = m / p
        if spec.demand_class == "intermittent":
            sizes = 1 + rng.poisson(max(size_mean - 1.0, 0.0), size=n)
        else:
            sigma = spec.size_sigma
            sizes = np.rint(rng.lognormal(np.log(size_mean) - sigma**2 / 2.0, sigma, size=n)).astype(np.int64)
        sizes = np.maximum(sizes, 1)
        demand[occurs] = sizes[occurs]

    for w in spec.spike_weeks:
        spike = int(rng.integers(4, 9)) * max(round(m), 1)
        demand[w] = max(demand[w], spike)
    return demand


def simulate_inventory(
    spec: ItemSpec, demand: np.ndarray, periods: list[date], rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, list[dict], list[dict]]:
    """Periodic-review order-up-to replenishment with censoring at stock-outs.

    Returns recorded consumption, closing stock per week, receipts and the
    orders still open after the last week (planned receipts).
    """
    n = len(demand)
    lead = spec.lead_time_weeks
    base = max(spec.mean_weekly_demand, 0.25)
    cycle = spec.order_cycle_weeks

    consumption = np.zeros(n, dtype=np.int64)
    closing = np.zeros(n, dtype=np.int64)
    receipts: list[dict] = []
    pending: list[dict] = []
    on_hand = math.ceil(base * (lead + 1 + spec.safety_weeks + cycle) + 2.0 * base / spec.occurrence_probability)

    blocks = {start: target for start, target in spec.delivery_blocks}
    block_remaining: int | None = None  # stock-out weeks still to record in the active block
    block_started = 0

    for t in range(n):
        if block_remaining is None and t in blocks:
            block_remaining, block_started = blocks[t], t

        if block_remaining is None:
            arrived = [o for o in pending if o["due"] <= t]
            pending = [o for o in pending if o["due"] > t]
        else:
            arrived = []  # deliveries are held while the episode lasts
        for order in arrived:
            on_hand += order["quantity"]
            received_on = periods[t] + timedelta(days=int(rng.integers(0, 5)))
            receipts.append(
                {"item_code": spec.code, "received_on": received_on, "quantity": order["quantity"], "supplier": spec.supplier}
            )

        served = min(int(demand[t]), on_hand)
        on_hand -= served
        consumption[t] = served
        closing[t] = on_hand

        if block_remaining is not None:
            if on_hand == 0:
                block_remaining -= 1
            if block_remaining <= 0 or t - block_started >= MAX_BLOCK_WEEKS:
                block_remaining = None  # held deliveries arrive from the next week

        # review: the pharmacy estimates the weekly rate and its variability from
        # the trailing 26 weeks, ignoring weeks it knows it was out of stock, and
        # keeps a safety stock of `safety_weeks` of demand plus one standard
        # deviation of demand over the lead time
        lo = max(0, t - 25)
        known = consumption[lo : t + 1][closing[lo : t + 1] > 0]
        rate = max(float(known.mean()) if len(known) else base, base / 2.0)
        sd = float(known.std()) if len(known) >= 4 else base
        safety_stock = spec.safety_weeks * rate + sd * math.sqrt(lead + 1)
        reorder_point = math.ceil(rate * (lead + 1) + safety_stock)
        order_up_to = math.ceil(reorder_point + rate * cycle)
        position = on_hand + sum(o["quantity"] for o in pending)
        if position <= reorder_point:
            pending.append({"placed": t, "due": t + lead, "quantity": int(max(order_up_to - position, 1))})

    planned: list[dict] = []
    for order in pending:
        # an order still held by a delayed-delivery episode is re-expected next week
        due = max(order["due"], n)
        expected_on = periods[-1] + timedelta(days=7 * (due - (n - 1)) + int(rng.integers(0, 5)))
        planned.append(
            {"item_code": spec.code, "expected_on": expected_on, "quantity": order["quantity"], "supplier": spec.supplier}
        )
    return consumption, closing, receipts, planned


def observed_stats(consumption: np.ndarray, closing: np.ndarray) -> dict:
    """Syntetos-Boylan labels and quality counters of the recorded series."""
    n = len(consumption)
    nonzero = consumption[consumption > 0]
    n_nonzero = len(nonzero)
    adi = float(n / n_nonzero) if n_nonzero else None
    if n_nonzero >= 2:
        mean = float(nonzero.mean())
        cv2 = float(nonzero.var(ddof=1) / (mean * mean)) if mean > 0 else None
    else:
        cv2 = None
    if adi is None or cv2 is None:
        observed_class = "insufficient"
    elif adi < ADI_CUTOFF:
        observed_class = "smooth" if cv2 < CV2_CUTOFF else "erratic"
    else:
        observed_class = "intermittent" if cv2 < CV2_CUTOFF else "lumpy"
    stockout = closing == 0
    return {
        "weeks": n,
        "nonzero_weeks": n_nonzero,
        "zero_share": round(float((consumption == 0).mean()), 3),
        "adi": round(adi, 3) if adi is not None else None,
        "cv2": round(cv2, 3) if cv2 is not None else None,
        "observed_class": observed_class,
        "total_consumption": int(consumption.sum()),
        "stock_out_weeks": int(stockout.sum()),
        "_stockout_mask": stockout,
    }


def stockout_episodes(mask: np.ndarray, periods: list[date]) -> list[dict]:
    episodes: list[dict] = []
    start: int | None = None
    for i, flag in enumerate(list(mask) + [False]):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            episodes.append({"first_week": periods[start].isoformat(), "last_week": periods[i - 1].isoformat(), "weeks": i - start})
            start = None
    return episodes


def aggregate_deliveries(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """One row per item, booking day and supplier, as the import format requires.

    Several orders of one item can arrive in the same week and draw the same
    booking day; ``receipts.csv`` and ``planned_receipts.csv`` carry such
    deliveries as one summed row (data specification, section 3.3 and V-09).
    """
    out = df.copy()
    out[date_col] = out[date_col].map(lambda d: d.isoformat())
    out = out.groupby(["item_code", date_col, "supplier"], as_index=False, sort=False)["quantity"].sum()
    out = out[["item_code", date_col, "quantity", "supplier"]]
    return out.sort_values([date_col, "item_code"], kind="stable").reset_index(drop=True)


def generate(
    n_items: int = DEFAULT_ITEMS,
    n_weeks: int = DEFAULT_WEEKS,
    seed: int = DEFAULT_SEED,
    end: date | str = DEFAULT_END,
) -> tuple[dict[str, pd.DataFrame], dict]:
    """Build all tables in memory. Returns (frames, metadata)."""
    end_date = date.fromisoformat(end) if isinstance(end, str) else end
    validate_args(n_items, n_weeks, end_date)
    rng = np.random.default_rng(seed)
    periods = weekly_periods(end_date, n_weeks)
    period_str = [p.isoformat() for p in periods]
    specs = build_item_specs(n_items, n_weeks, rng)

    consumption_rows: list[dict] = []
    stock_rows: list[dict] = []
    truth_rows: list[dict] = []
    receipt_rows: list[dict] = []
    planned_rows: list[dict] = []
    item_rows: list[dict] = []
    item_meta: list[dict] = []

    for spec in specs:
        demand = simulate_demand(spec, periods, rng)
        consumption, closing, receipts, planned = simulate_inventory(spec, demand, periods, rng)
        stats = observed_stats(consumption, closing)
        mask = stats.pop("_stockout_mask")
        stats["stock_out_episodes"] = stockout_episodes(mask, periods)
        stats["censored_demand_units"] = int((demand - consumption).sum())

        for t in range(n_weeks):
            consumption_rows.append(
                {
                    "item_code": spec.code,
                    "item_name": spec.name,
                    "unit": spec.unit,
                    "period_start": period_str[t],
                    "quantity": int(consumption[t]),
                }
            )
            stock_rows.append({"item_code": spec.code, "period_start": period_str[t], "quantity_on_hand": int(closing[t])})
            truth_rows.append(
                {
                    "item_code": spec.code,
                    "period_start": period_str[t],
                    "demand": int(demand[t]),
                    "quantity": int(consumption[t]),
                    "is_stock_out": "true" if mask[t] else "false",
                }
            )
        receipt_rows.extend(receipts)
        planned_rows.extend(planned)
        item_rows.append(
            {
                "item_code": spec.code,
                "item_name": spec.name,
                "unit": spec.unit,
                "group": spec.group,
                "is_active": "true",
                "supplier": spec.supplier,
                "lead_time_days": 7 * spec.lead_time_weeks,
            }
        )
        meta = asdict(spec)
        meta["delivery_blocks"] = [
            {"first_week": period_str[b[0]], "target_stock_out_weeks": b[1]} for b in spec.delivery_blocks
        ]
        meta["spike_weeks"] = [period_str[w] for w in spec.spike_weeks]
        meta["observed"] = stats
        item_meta.append(meta)

    consumption_df = pd.DataFrame(consumption_rows, columns=["item_code", "item_name", "unit", "period_start", "quantity"])
    stock_df = pd.DataFrame(stock_rows, columns=["item_code", "period_start", "quantity_on_hand"])
    truth_df = pd.DataFrame(truth_rows, columns=["item_code", "period_start", "demand", "quantity", "is_stock_out"])
    receipts_df = pd.DataFrame(receipt_rows, columns=["item_code", "received_on", "quantity", "supplier"])
    planned_df = pd.DataFrame(planned_rows, columns=["item_code", "expected_on", "quantity", "supplier"])
    items_df = pd.DataFrame(
        item_rows, columns=["item_code", "item_name", "unit", "group", "is_active", "supplier", "lead_time_days"]
    )

    receipts_df = aggregate_deliveries(receipts_df, "received_on")
    planned_df = aggregate_deliveries(planned_df, "expected_on")

    frames = {
        "consumption.csv": consumption_df,
        "stock.csv": stock_df,
        "receipts.csv": receipts_df,
        "planned_receipts.csv": planned_df,
        "items.csv": items_df,
        "true_demand.csv": truth_df,
    }
    metadata = {
        "dataset": "PharmaStock synthetic development dataset",
        "generator": "forecasting/data/generate_synthetic.py",
        "generator_version": GENERATOR_VERSION,
        "parameters": {"items": n_items, "weeks": n_weeks, "seed": seed, "end": end_date.isoformat()},
        "period": {"first_week": period_str[0], "last_week": period_str[-1], "weeks": n_weeks},
        "counts": {
            "items": n_items,
            "consumption_rows": len(consumption_df),
            "stock_rows": len(stock_df),
            "receipt_rows": len(receipts_df),
            "planned_receipt_rows": len(planned_df),
            "stock_out_weeks": int(sum(m["observed"]["stock_out_weeks"] for m in item_meta)),
            "items_with_stock_outs": int(sum(1 for m in item_meta if m["observed"]["stock_out_weeks"] > 0)),
            "demand_classes": {c: int(sum(1 for m in item_meta if m["demand_class"] == c)) for c in DEMAND_CLASSES},
        },
        "items": item_meta,
    }
    return frames, metadata


def write_outputs(out_dir: Path, frames: dict[str, pd.DataFrame], metadata: dict, write_truth: bool, omit_zero_rows: bool) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, df in frames.items():
        if name == "true_demand.csv" and not write_truth:
            continue
        if name == "consumption.csv" and omit_zero_rows:
            df = df[df["quantity"] > 0]
        path = out_dir / name
        df.to_csv(path, index=False, lineterminator="\n", encoding="utf-8")
        written.append(path)
    meta_path = out_dir / "dataset.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(meta_path)
    return written


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        end_date = date.fromisoformat(args.end)
        frames, metadata = generate(args.items, args.weeks, args.seed, end_date)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    written = write_outputs(args.out, frames, metadata, args.write_truth, args.omit_zero_rows)
    counts = metadata["counts"]
    total_kb = sum(p.stat().st_size for p in written) / 1024
    print(f"PharmaStock synthetic dataset written to {args.out}")
    print(f"  items={args.items} weeks={args.weeks} seed={args.seed} "
          f"period={metadata['period']['first_week']}..{metadata['period']['last_week']}")
    print(f"  consumption rows={counts['consumption_rows']} stock rows={counts['stock_rows']} "
          f"receipts={counts['receipt_rows']} planned receipts={counts['planned_receipt_rows']}")
    print(f"  stock-out weeks={counts['stock_out_weeks']} in {counts['items_with_stock_outs']} items; "
          f"demand classes={counts['demand_classes']}")
    print(f"  files: {', '.join(p.name for p in written)} ({total_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
