# Synthetic development dataset

Task: PHA2-15 · Last updated: 2026-10-18 · Author: Evelina Penkova

This folder holds the generator of the PharmaStock synthetic development dataset and a small generated sample. The dataset exists because access to real data from a partner healthcare organization is still pending (see `docs/data/data-specification.md`, section 11). **Every result obtained on these files is a result on synthetic data and is reported as such.**

## Contents

| Path | Purpose |
|---|---|
| `generate_synthetic.py` | Generator script (Python 3.12, pandas, numpy). Documented in `docs/data/data-specification.md`, section 10 |
| `sample/consumption.csv` | Weekly recorded consumption per item: `item_code,item_name,unit,period_start,quantity` |
| `sample/stock.csv` | Closing stock balance per item and week: `item_code,period_start,quantity_on_hand` |
| `sample/receipts.csv` | Deliveries booked into stock: `item_code,received_on,quantity,supplier` |
| `sample/planned_receipts.csv` | Orders still open after the last week: `item_code,expected_on,quantity,supplier` |
| `sample/items.csv` | Catalogue seed: `item_code,item_name,unit,group,is_active,supplier,lead_time_days` (reference file, not an import type) |
| `sample/dataset.json` | Generation parameters, period, row counts and per-item ground truth (demand class, mean demand, seasonality, trend, lead time, delayed-delivery episodes, spike weeks) with observed statistics (ADI, CV², stock-out weeks and episodes, censored demand) |

The four CSV import files follow the formats of `docs/data/data-specification.md`, section 3, exactly: UTF-8, comma delimiter, ISO dates, `period_start` is always a Monday, quantities are integers in the catalogue unit, and deliveries of one item booked on the same day from the same supplier are one summed row (rule V-09).

## Regenerating the sample

From the repository root:

```
python forecasting/data/generate_synthetic.py --items 20 --weeks 104 --seed 42 --out forecasting/data/sample
```

The generator is deterministic: the same arguments reproduce byte-identical files, so a regenerated sample must not produce a Git diff. Do not edit the files in `sample/` by hand; change the generator and regenerate instead, and keep the sample below 300 KB.

Other useful commands:

```
# default development dataset: 30 items, 3 years, written to ./synthetic
# (synthetic/ and synthetic-large/ are ignored by Git; only sample/ is committed)
python forecasting/data/generate_synthetic.py

# include the uncensored demand for censored-demand experiments
python forecasting/data/generate_synthetic.py --items 20 --weeks 104 --seed 42 --out synthetic --write-truth

# movement-only export (zero-consumption rows omitted) to test the import filling rules
python forecasting/data/generate_synthetic.py --omit-zero-rows --out synthetic

# dataset for performance measurements (NFR-01, NFR-02)
python forecasting/data/generate_synthetic.py --items 1000 --weeks 156 --out synthetic-large
```

`python forecasting/data/generate_synthetic.py --help` lists all arguments (`--items`, `--weeks`, `--seed`, `--out`, `--end`, `--write-truth`, `--omit-zero-rows`).

## Sample statistics (`--items 20 --weeks 104 --seed 42`)

| Statistic | Value |
|---|---|
| Period | 2024-10-21 … 2026-10-12 (104 weeks, `period_start` of the last week = `--end` default) |
| Rows | consumption 2,080; stock 2,080; receipts 330; planned receipts 18 |
| Size | about 210 KB in total (the generator prints the exact size) |
| Demand classes (generation truth) | smooth 6, intermittent 5, erratic 3, lumpy 6 |
| Seasonal / trending / spiking items | 5 / 8 / 5 |
| Items with delayed-delivery episodes | 9 |
| Stock-out weeks (`quantity_on_hand = 0`) | 78 of 2,080 item-weeks (3.8 %) in 14 items; 6 items never out of stock |
| Censored demand | 3,050 units of true demand not recorded (2.5 % of 121,641 units consumed) |
| Zero-consumption weeks | 854 (41 %) |
| Suppliers / lead times | SK-Pharmacy 14 items (28–56 days), Distributor A 4 and Distributor B 2 (7–21 days) |

## What the data look like

- A **smooth** item (for example `MED-0001`, amoxicillin) is consumed every week with moderate variation and a winter peak.
- An **intermittent** item (for example `MED-0002`, ceftriaxone in this sample) has long runs of zero weeks with small quantities in between.
- A **lumpy** item (for example `MED-0004`) combines zero runs with occasional large quantities; such items run out most often when the lead time is long.
- During a **delayed-delivery episode** the stock balance falls to zero, the recorded consumption is cut to what was on the shelf and is then zero for one to four weeks although demand continued. These are the censored-demand weeks that FR-17 flags; `true_demand.csv` (with `--write-truth`) shows what the demand would have been.
- `closing(t) = closing(t-1) + receipts(t) - consumption(t)` holds for every item and week, so the import can be checked for balance consistency.

## Limitations

The dataset is a simplified model: one supplier per item, no expiry, write-offs or transfers, a single annual seasonal pattern and delayed deliveries as the only cause of long stock-outs. See `docs/data/data-specification.md`, section 10.5. Parameters of the demand classes will be re-tuned once real data are available.
