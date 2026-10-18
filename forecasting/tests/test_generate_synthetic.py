"""Tests for forecasting/data/generate_synthetic.py (PHA2-15, NFR-05).

The generator is a stand-alone script, so it is run through ``subprocess``
and its output is read with the standard ``csv`` module: the tests depend
neither on the forecasting package nor on its installation.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "data" / "generate_synthetic.py"

# Small dataset: 5 items, 20 weeks, seed 1. The seed is part of the fixture
# because the stock-out assertion below depends on the drawn delivery blocks.
ITEMS = 5
WEEKS = 20
SEED = 1
LAST_WEEK = date(2026, 10, 12)  # generator default ``--end``, a Monday

IMPORT_FILES = ("consumption.csv", "stock.csv", "receipts.csv", "planned_receipts.csv")
HEADERS = {
    "consumption.csv": ["item_code", "item_name", "unit", "period_start", "quantity"],
    "stock.csv": ["item_code", "period_start", "quantity_on_hand"],
    "receipts.csv": ["item_code", "received_on", "quantity", "supplier"],
    "planned_receipts.csv": ["item_code", "expected_on", "quantity", "supplier"],
}
MONDAY = 0


def run_generator(out_dir: Path) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--items",
        str(ITEMS),
        "--weeks",
        str(WEEKS),
        "--seed",
        str(SEED),
        "--out",
        str(out_dir),
    ]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def read_header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def week_of(day: date) -> date:
    """Monday of the ISO week that contains ``day``."""
    return day - timedelta(days=day.weekday())


@pytest.fixture(scope="module")
def dataset(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out_dir = tmp_path_factory.mktemp("synthetic")
    result = run_generator(out_dir)
    assert result.returncode == 0, result.stderr
    return out_dir


def test_same_arguments_give_byte_identical_files(tmp_path: Path) -> None:
    first, second = tmp_path / "first", tmp_path / "second"
    for out_dir in (first, second):
        result = run_generator(out_dir)
        assert result.returncode == 0, result.stderr

    names = sorted(path.name for path in first.iterdir())
    assert names == sorted(path.name for path in second.iterdir())
    assert set(IMPORT_FILES) <= set(names)
    assert {"items.csv", "dataset.json"} <= set(names)
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_import_files_have_the_agreed_headers(dataset: Path) -> None:
    for name in IMPORT_FILES:
        assert read_header(dataset / name) == HEADERS[name], name


def test_every_period_start_is_a_monday_of_the_weekly_grid(dataset: Path) -> None:
    expected = [LAST_WEEK - timedelta(days=7 * (WEEKS - 1 - i)) for i in range(WEEKS)]
    assert all(day.weekday() == MONDAY for day in expected)

    for name in ("consumption.csv", "stock.csv"):
        rows = read_rows(dataset / name)
        assert len(rows) == ITEMS * WEEKS, name
        per_item: dict[str, list[date]] = defaultdict(list)
        for row in rows:
            day = date.fromisoformat(row["period_start"])
            assert day.weekday() == MONDAY, (name, row)
            per_item[row["item_code"]].append(day)
        assert len(per_item) == ITEMS, name
        for code, days in per_item.items():
            assert sorted(days) == expected, (name, code)


def test_closing_stock_follows_receipts_and_consumption(dataset: Path) -> None:
    consumption = {
        (row["item_code"], row["period_start"]): int(row["quantity"])
        for row in read_rows(dataset / "consumption.csv")
    }
    closing = {
        (row["item_code"], row["period_start"]): int(row["quantity_on_hand"])
        for row in read_rows(dataset / "stock.csv")
    }
    assert consumption.keys() == closing.keys()

    # Receipts are booked on a working day of the week in which they arrive;
    # the week's total is what entered stock before that week's consumption.
    receipts: dict[tuple[str, str], int] = defaultdict(int)
    first_week = min(date.fromisoformat(period) for _, period in closing)
    for row in read_rows(dataset / "receipts.csv"):
        received_on = date.fromisoformat(row["received_on"])
        assert first_week <= received_on <= LAST_WEEK + timedelta(days=6), row
        quantity = int(row["quantity"])
        assert quantity > 0, row
        receipts[(row["item_code"], week_of(received_on).isoformat())] += quantity

    per_item: dict[str, list[str]] = defaultdict(list)
    for code, period in closing:
        per_item[code].append(period)

    for code, periods in per_item.items():
        periods.sort()
        for t, period in enumerate(periods):
            key = (code, period)
            assert consumption[key] >= 0 and closing[key] >= 0, key
            if t == 0:
                # The opening stock before the first week is not exported;
                # it is what the first week's balance implies, and it is not negative.
                assert closing[key] + consumption[key] - receipts[key] >= 0, key
                continue
            previous = (code, periods[t - 1])
            assert closing[key] == closing[previous] + receipts[key] - consumption[key], key


def test_dataset_contains_a_stock_out_week_with_zero_consumption(dataset: Path) -> None:
    consumption = {
        (row["item_code"], row["period_start"]): int(row["quantity"])
        for row in read_rows(dataset / "consumption.csv")
    }
    closing = {
        (row["item_code"], row["period_start"]): int(row["quantity_on_hand"])
        for row in read_rows(dataset / "stock.csv")
    }

    stock_out_weeks = [key for key, on_hand in closing.items() if on_hand == 0]
    assert stock_out_weeks, "the fixture must contain stock-out weeks"
    assert any(consumption[key] == 0 for key in stock_out_weeks)
