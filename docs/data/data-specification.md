# PharmaStock — Data Specification

Task: PHA2-15 · Last updated: 2026-10-20 · Status: draft v0.2 · Author: Evelina Penkova

---

## 1. Purpose and scope

This document defines the data that enters PharmaStock and the data the forecasting module works with:

- the import file formats (FR-01) and their columns, units and conventions;
- the validation rules applied on import (FR-02) and how validation results are reported;
- the treatment of missing weeks and the derivation of the stock-out flag (FR-17) that marks censored demand;
- the content of the data-quality summary per import (FR-18);
- the synthetic development dataset used until real data are available, and the status of real-data access.

The import formats are the single agreed interface between the accounting exports of a healthcare organization and the system. The backend (`POST /api/v1/imports`) accepts these formats, stores the rows in the entities listed in section 4, and builds from them the history that the forecasting module receives (`forecasting.api.forecast_items(history, horizon, config)`). Item-level aggregated data only are handled: no patient-level, prescription-level or personal data are imported, stored or processed (NFR-04).

Related documents: `docs/requirements.md` (FR-01, FR-02, FR-17, FR-18 and their acceptance criteria), `docs/architecture/database-schema.md` (entities), `docs/architecture/api-contract.md` (import endpoints), `docs/verification-and-evaluation-plan.md` (how the dataset is used in experiments), `forecasting/data/README.md` (sample dataset).

## 2. Conventions

| Topic | Convention |
|---|---|
| Time step | One week. A week runs from Monday to Sunday. `period_start` is the ISO date of the Monday of the week (`YYYY-MM-DD`). Daily exports must be aggregated before import: consumption summed per item and ISO week, stock = closing balance of the last day of the week; rows whose `period_start` is not a Monday are rejected (V-07). |
| Quantities | Numbers in the catalogue unit of the item (`medicine_item.unit`: pack, vial, ampoule, bottle, syringe, cartridge, inhaler, ...). Decimal separator is a dot; thousands separators are not allowed. Countable units are integers; decimals are accepted for units such as litre or kilogram. |
| Consumption | `quantity` in `consumption.csv` is the quantity issued from the pharmacy to departments or patients during the week. It is recorded consumption, not demand: when the item was out of stock, recorded consumption is lower than demand (section 7). |
| Stock | `quantity_on_hand` in `stock.csv` is the closing balance at the end of the week starting on `period_start` (after the receipts and consumption of that week). An export that gives opening balances must be shifted by one week before import. |
| Receipts | `received_on` is the calendar date on which the delivery was booked into stock; it is assigned to the week that contains it. A receipt is available for consumption in the same week. |
| Planned receipts | `expected_on` is the expected delivery date of an open order; it is normally after the last imported week. |
| Item identity | `item_code` is the unique code of the item in the organization's catalogue (`medicine_item.code`), trimmed, at most 64 characters, case-sensitive. The code is the join key of all files. |
| Suppliers | `supplier` is the supplier name as a string (`supplier.name`); the central distributor is written as `SK-Pharmacy`. Lead times are maintained per item in the catalogue (`item_supplier.lead_time_days`), not in the import files. |
| Encoding and format | CSV: UTF-8 (a byte-order mark is tolerated), comma delimiter, header row with the exact column names below, optional columns may be omitted. XLSX: the first sheet with the same header row. Extra columns are ignored with a warning (V-02). |
| Dates | ISO `YYYY-MM-DD` only. |
| Booleans (reference files) | `true` / `false`, lower case. |

## 3. Import files

Four import types are accepted (`import_batch.source_type`: `consumption`, `stock`, `receipts`, `planned_receipts`). One file holds one type.

### 3.1 `consumption.csv`

Header: `item_code,item_name,unit,period_start,quantity`

| Column | Type | Required | Description | Stored in |
|---|---|---|---|---|
| `item_code` | string | yes | Item code in the catalogue | `consumption_record.item_id` (looked up) |
| `item_name` | string | yes | Item name as in the export; used to create or check catalogue entries | `medicine_item.name` (on creation only) |
| `unit` | string | yes | Catalogue unit of the quantity | `medicine_item.unit` (on creation only) |
| `period_start` | date | yes | Monday of the week | `consumption_record.period_start` |
| `quantity` | number ≥ 0 | yes | Quantity issued during the week, in `unit` | `consumption_record.quantity` |

One row per item and week. Weeks with zero consumption may be present as rows with `quantity` = 0 or omitted (section 6).

### 3.2 `stock.csv`

Header: `item_code,period_start,quantity_on_hand`

| Column | Type | Required | Description | Stored in |
|---|---|---|---|---|
| `item_code` | string | yes | Item code in the catalogue | `stock_snapshot.item_id` (looked up) |
| `period_start` | date | yes | Monday of the week whose closing balance is given | `stock_snapshot.period_start` |
| `quantity_on_hand` | number ≥ 0 | yes | Closing stock balance of the week, in the catalogue unit | `stock_snapshot.quantity_on_hand` |

One row per item and week. `stock_snapshot.is_stock_out` is derived on import (section 7), it is not a column of the file.

### 3.3 `receipts.csv`

Header: `item_code,received_on,quantity,supplier`

| Column | Type | Required | Description | Stored in |
|---|---|---|---|---|
| `item_code` | string | yes | Item code in the catalogue | `receipt.item_id` (looked up) |
| `received_on` | date | yes | Date the delivery was booked into stock | `receipt.received_on` |
| `quantity` | number > 0 | yes | Delivered quantity, in the catalogue unit | `receipt.quantity` |
| `supplier` | string | yes | Supplier name | `receipt.supplier_id` (looked up or created, V-11) |

One row per delivery line. Two deliveries of the same item on the same day from the same supplier are exported as one summed row.

### 3.4 `planned_receipts.csv`

Header: `item_code,expected_on,quantity,supplier`

| Column | Type | Required | Description | Stored in |
|---|---|---|---|---|
| `item_code` | string | yes | Item code in the catalogue | `planned_receipt.item_id` (looked up) |
| `expected_on` | date | yes | Expected delivery date | `planned_receipt.expected_on` |
| `quantity` | number > 0 | yes | Ordered quantity, in the catalogue unit | `planned_receipt.quantity` |
| `supplier` | string | yes | Supplier name | `planned_receipt.supplier_id` |

Imported planned receipts get `planned_receipt.status = planned`. They can also be recorded one by one in the web interface (FR-10).

### 3.5 Catalogue reference file (proposed, not an import type yet)

The catalogue (FR-03) and lead times (FR-04) are maintained in the application. To seed them for development and tests, the synthetic dataset ships `items.csv` with the header `item_code,item_name,unit,group,is_active,supplier,lead_time_days`, which maps one to one onto `medicine_item` (`code`, `name`, `unit`, `group`, `is_active`) and `item_supplier` (`supplier_id`, `lead_time_days`, `is_primary = true`). Whether this file becomes a fifth import type is an open question (section 12, Q-3).

## 4. Mapping to data entities

| Entity | Filled from | Key / uniqueness | Notes |
|---|---|---|---|
| `medicine_item` | catalogue (FR-03); `consumption.csv` rows when item creation on import is enabled | `code` unique | `group` is used for error analysis per medicine group in the evaluation |
| `supplier` | catalogue (FR-04); supplier names in `receipts.csv` / `planned_receipts.csv` | `name` unique | |
| `item_supplier` | catalogue (FR-04) | (`item_id`, `supplier_id`) | `lead_time_days` is the input of the risk calculation (FR-08) |
| `import_batch` | every upload | `id` | `summary_json` holds the validation report and the data-quality summary (section 8) |
| `consumption_record` | `consumption.csv` | (`item_id`, `period_start`) unique | `import_batch_id` references the batch that provided the row |
| `stock_snapshot` | `stock.csv` | (`item_id`, `period_start`) unique | `is_stock_out` derived (section 7) |
| `receipt` | `receipts.csv` | `id`; no uniqueness beyond V-09 | |
| `planned_receipt` | `planned_receipts.csv`, FR-10 | `id` | `status`: `planned`, `received`, `cancelled` |

Weekly history used by the forecasting module is built per item from `consumption_record` and `stock_snapshot` (section 9).

## 5. Validation rules (FR-02)

Validation is all-or-nothing per file (AC-02.4): if any rule with severity **error** fails, no rows of the file are stored, the `import_batch` is kept with status `failed` and the full list of findings (AC-01.3). Findings with severity **warning** do not block the import; they are stored in the batch summary and shown to the user (AC-02.3). Every row-level finding names the row number, the column and the offending value (AC-02.2).

| ID | Applies to | Rule | Severity | Message (template) |
|---|---|---|---|---|
| V-01 | all | The file is parseable: UTF-8 CSV with a comma delimiter, or XLSX with a first sheet | error | `file cannot be parsed: <reason>` |
| V-02 | all | The header row contains every required column of the import type (names compared exactly and case-sensitively; column order is not significant); unknown columns are ignored | error / warning for extra columns | `missing required column(s): <names>` / `column <name> ignored` |
| V-03 | all | The file has at least one data row | error | `file contains no data rows` |
| V-04 | all | `item_code` is non-empty after trimming and at most 64 characters | error | `row <n>: item_code is empty or too long` |
| V-05 | all | `item_code` exists in the catalogue. Default: unknown codes are rejected. Planned import option `create_items` (only for `consumption.csv`, which carries `item_name` and `unit`): unknown codes create catalogue entries; see Q-1 | error | `row <n>: unknown item <code>` |
| V-06 | all | `period_start`, `received_on`, `expected_on` are valid ISO dates | error | `row <n>: <column> is not a date: <value>` |
| V-07 | `consumption`, `stock` | `period_start` is a Monday; daily rows are rejected, aggregation to weeks is the responsibility of the export step (section 2). Whether a `granularity=daily` import option is needed is open question Q-5 | error | `row <n>: period_start <value> is not a Monday` |
| V-08 | all | `quantity` / `quantity_on_hand` is a number with a dot decimal separator and is not negative; `quantity` in receipts and planned receipts is greater than zero | error | `row <n>: negative quantity <value>` / `row <n>: quantity is not a number: <value>` |
| V-09 | all | No duplicate key inside the file: (`item_code`, `period_start`) in consumption and stock; identical (`item_code`, `received_on` or `expected_on`, `supplier`) rows in receipts and planned receipts | error | `row <n>: duplicate period for item <code> (first seen in row <m>)` |
| V-10 | `consumption` | `item_name` or `unit` differs from the catalogue entry of `item_code`; the catalogue is not changed | warning | `row <n>: item_name/unit differs from catalogue` |
| V-11 | `receipts`, `planned_receipts` | `supplier` is non-empty; an unknown supplier name creates a new `supplier` record (proposed default, see Q-2). Note: `docs/architecture/api-contract.md` currently lists an unknown supplier as a blocking error (`422 IMPORT_VALIDATION_FAILED`, error code `unknown_supplier`); the two documents are aligned when Q-2 is decided | error (empty) / warning (created) | `row <n>: supplier is empty` / `supplier <name> created` |
| V-12 | `consumption`, `stock`, `receipts` | Dates are not in the future: `period_start` is not after the Monday of the import week, `received_on` is not after the import date | error | `row <n>: <column> <value> is in the future` |
| V-13 | `planned_receipts` | `expected_on` is not in the past | warning | `row <n>: expected_on <value> is in the past` |
| V-14 | all | A non-integer quantity for an item whose unit is countable (pack, vial, ampoule, bottle, syringe, cartridge, inhaler) | warning | `row <n>: non-integer quantity <value> for unit <unit>` |
| V-15 | `consumption`, `stock` | Rows whose (`item_code`, `period_start`) already exist from an earlier batch replace the earlier rows (last import wins; decided, `docs/requirements.md` section 5.5.1). The backend writes them with `INSERT ... ON CONFLICT DO UPDATE` on the unique key, so a re-import of a period updates the stored rows in place; the number of updated rows is reported in the batch summary (see Q-4 for the remaining question) | info | `<rows_replaced> existing rows updated` |

The rule set is implemented by the backend import service (DIP task to be assigned to Abzal Bakhytov). The forecasting module applies V-04, V-06, V-08 and V-09 plus the contiguous-index check (no duplicate and no missing Monday per item) to any history it receives (`forecasting/forecasting/data/validation.py`, PHA2-16; NFR-06): malformed input raises a clear error instead of producing a forecast. V-05 (catalogue lookup) and V-07 (rejection of daily rows at file level) are backend-only; the module keeps its own check that every `period_start` is a Monday (`period_not_monday`).

## 6. Treatment of missing weeks

Accounting exports often list only movements, so weeks without consumption are missing rather than zero. The rules below make the stored history a complete weekly grid per item.

| Situation | Treatment | Reported in summary (FR-18) |
|---|---|---|
| Coverage of a consumption file | The covered period of a file is `[min(period_start), max(period_start)]` over all rows of the file | `coverage.first_week`, `coverage.last_week` |
| (item, week) missing inside the covered period of a consumption file | Stored as `quantity = 0` for that item and week (explicit zero, flagged `filled = true` in the batch summary, not in the entity) | `gaps.filled_zero_weeks` per item |
| Leading weeks before the first non-zero consumption of an item | Kept as zeros in the stored history. Trimming of the leading zeros before the first observed consumption is planned for the forecasting module, so that items introduced during the period are not learned as long zero runs; it is not part of package 0.1.0 and has no configuration key yet | `gaps.leading_zero_weeks` per item |
| Weeks after the last row of an item up to the end of the covered period | Stored as zeros, like any missing week inside the covered period | included in `filled_zero_weeks` |
| (item, week) missing in `stock.csv` | Not filled. No `stock_snapshot` row is created; the stock-out flag is derived only from observed snapshots (section 7). Item pages carry the last known balance forward for display and mark it as carried forward | `gaps.missing_stock_weeks` per item |
| Stock snapshot older than two weeks at the time of a forecast run | The risk calculation uses the latest snapshot and records its date; the item is marked "stock outdated" in the risk list | `stock_age_weeks` |
| Receipts and planned receipts | No weekly grid; a missing week means no delivery | — |
| Weeks between the end of one import and the start of the next | Filled with `quantity = 0` like any other missing week. The forecasting module's `make_regular_weekly` fills every week absent from an item's series, flags it (`is_filled = true`) and counts it per item (`n_filled_weeks`, reported in the run warnings); the input frame of the module never contains missing values (NaN). Gaps longer than one week are listed in the summary so that the user can check the exports | `gaps.history_gaps` (ranges) |

## 7. Stock-out flag derivation (FR-17)

Zero consumption during a stock-out is censored demand: demand existed but could not be served, so the recorded quantity is not an observation of demand. The flag makes this explicit.

1. **Primary rule (AC-17.1).** For every imported stock snapshot, `stock_snapshot.is_stock_out = (quantity_on_hand == 0)`. A week is a stock-out week for an item if its snapshot has zero quantity on hand.
2. **Meaning of the recorded consumption in a flagged week.** The recorded `quantity` is a lower bound of demand: the stock ran out during the week (partial week, `quantity > 0`) or was empty for the whole week (`quantity = 0`, demand unknown).
3. **Weeks without a snapshot** are never flagged; they are counted as missing stock weeks (section 6) and the item is listed in the summary when a zero-consumption run coincides with missing snapshots.
4. **Hand-off to the forecasting module (AC-17.2).** The history frame (section 9) carries `is_stock_out` per week. The default handling is to treat flagged weeks as missing observations rather than as zeros (FQ-10): with `censoring_method: exclude` they are removed from the training series and from the metrics, as implemented in the experiment runner (`forecasting/experiments/run_baselines.py`); package 0.1.0 itself only counts them (`n_censored_weeks`), and the exclusion when fitting is planned there. The alternative treatment, imputation by the item's expected demand (FQ-10; `censoring_method: impute`), is planned and is compared with exclusion in the experiments (open question Q8 of the requirements). The chosen method is recorded with every run and documented in `forecasting/README.md`.
5. **Planned heuristic (not implemented, to be validated on real data).** For items consumed in most weeks, an unusually long run of zero consumption without a corresponding zero snapshot is reported as a *suspected* stock-out in the data-quality summary; it does not set the flag.
6. **Evaluation.** Stock-out weeks on the test period are the ground truth for the precision and recall of shortage alerts (`docs/verification-and-evaluation-plan.md`), and forecast quality is reported separately for items with and without stock-out weeks in their history.

## 8. Data-quality summary per import (FR-18)

The summary is computed after a successful import and stored in `import_batch.summary_json`; the web interface shows it after upload and on the import page (`GET /api/v1/imports/{id}`).

| Section | Content |
|---|---|
| `coverage` | First and last week, number of weeks, number of items in the file, number of rows imported, number of items affected (AC-01.4) |
| `gaps` | Per item: filled zero weeks, leading zero weeks, missing stock weeks, history gaps (section 6) |
| `stock_outs` | Per item: number of stock-out weeks and episodes (consecutive flagged weeks) in the file; suspected stock-outs (section 7, rule 5) |
| `outliers` | Per item: weeks whose quantity is greater than `outlier_factor` (default 5, key in `threshold_config`) times the item's median non-zero weekly quantity, evaluated only for items with at least 8 non-zero weeks (FR-18 definitions in `docs/requirements.md`); outliers are reported (`outliers`, `outliers_total`), not changed |
| `demand_profile` | Per item: share of zero weeks, average demand interval (ADI, weeks per non-zero week), squared coefficient of variation of non-zero quantities (CV²) and the resulting class — smooth (ADI < 1.32, CV² < 0.49), intermittent (ADI ≥ 1.32, CV² < 0.49), erratic (ADI < 1.32, CV² ≥ 0.49), lumpy (ADI ≥ 1.32, CV² ≥ 0.49) — following the Syntetos–Boylan categorisation of intermittent demand (reference to be given in `docs/literature-review.md`) |
| `warnings` | The validation warnings of section 5 |

## 9. Forecasting input frame

The backend builds the history that the forecasting module receives as a table with one row per item and week, a complete weekly grid per item from the item's first week to the last imported week:

| Column | Type | Description |
|---|---|---|
| `item_code` | string | Item code |
| `period_start` | date | Monday of the week |
| `quantity` | float ≥ 0 | Recorded consumption; `0` for weeks absent from the imports (section 6). The frame never contains missing values (NaN) |
| `is_stock_out` | boolean | Flag from section 7; `false` when no snapshot exists |
| `is_filled` | boolean | Added by the forecasting module: `true` for weeks that were absent from the input and filled with `quantity = 0` |

Rows are sorted by `item_code`, `period_start`. Weeks absent from an item's series (gaps between imports, zero weeks omitted by the export) are filled with `quantity = 0` by `forecasting.data.validation.make_regular_weekly`, flagged in `is_filled` and counted per item in `n_filled_weeks` of the result (`ForecastResult.item_info`, reported in `ForecastResult.warnings`); the series the models receive is contiguous and has no NaN. The schema and its checks (V-04, V-06, V-08, V-09, Monday check, complete grid, sorted, no duplicates; section 5) are implemented in `forecasting/forecasting/data/schema.py` and `forecasting/forecasting/data/validation.py` (implemented, PHA2-16). Per-item attributes needed by the risk calculation — current stock, planned receipts, lead time and safety stock — are not part of the frame; the backend passes them to the risk calculation separately (FR-08).

## 10. Synthetic development dataset

### 10.1 Why a synthetic dataset

Access to real historical data is being requested (section 11) and is not guaranteed in time for the first experiments. A documented synthetic dataset lets the team develop and test the import, the forecasting module, the risk calculation and the web interface in parallel, and gives a regression fixture whose ground truth is known. All results obtained on synthetic data are labelled as such; the dataset does not replace the evaluation on real data planned in `docs/verification-and-evaluation-plan.md`.

### 10.2 What the dataset models

The generator `forecasting/data/generate_synthetic.py` simulates a hospital pharmacy with the following properties (parameters are drawn per item from a seeded random generator and recorded in `dataset.json`):

| Aspect | How it is modelled |
|---|---|
| Catalogue | Up to 40 named items (international non-proprietary name, strength, form) in 15 medicine groups such as antibacterials, analgesics and antipyretics, infusion solutions, cardiovascular, anaesthetics; units pack, vial, ampoule, bottle, syringe, cartridge, inhaler. Items beyond 40 are named `Synthetic item NNNN`. Codes `MED-0001`, `MED-0002`, ... |
| Demand classes | Each item belongs to one Syntetos–Boylan class: **smooth** (consumed almost every week, low size variability), **intermittent** (many zero weeks, small regular sizes), **erratic** (almost every week, highly variable sizes), **lumpy** (many zero weeks, highly variable sizes). The first four items cover the four classes; the rest are drawn with weights 0.30 / 0.30 / 0.15 / 0.25 |
| Weekly demand | Bernoulli occurrence × demand size. Sizes: negative binomial (gamma–Poisson) for smooth, shifted Poisson (sizes ≥ 1) for intermittent, lognormal for erratic and lumpy. Quantities are non-negative integers in the catalogue unit |
| Seasonality | Multiplicative annual cosine with a winter peak for some antibacterials and antivirals, respiratory items and antipyretics (amplitude 0.20–0.60). For smooth and erratic items it scales the demand size, for intermittent and lumpy items the occurrence probability |
| Trend | A linear multiplicative trend between −30 % and +40 % over the whole period for about 40 % of the items |
| Outliers | One demand spike of 4–8 times the mean for about 30 % of the items (basis for the outlier report, FR-18) |
| Suppliers and lead times | About 60 % of the items are supplied by the central distributor `SK-Pharmacy` with lead times of 4–8 weeks (28–56 days); the rest by `Distributor A` or `Distributor B` with 1–3 weeks |
| Replenishment | Periodic review every week: the pharmacy estimates the weekly rate and its variability from the trailing 26 weeks of recorded consumption (ignoring weeks it knows it was out of stock), keeps a safety stock of 1–3 weeks of demand plus one standard deviation of demand over the lead time, and orders up to the reorder point plus 2–4 weeks of demand. Orders arrive after the lead time and become `receipts`; orders still open at the end of the history become `planned_receipts`. Deliveries of one item booked on the same day from the same supplier are written as one summed row (section 3.3, V-09) |
| Stock-outs and censoring | Delayed-delivery episodes for about 40 % of the items (1–2 per item): from a chosen week nothing is delivered until the item has been out of stock for 1–4 weeks (at most 20 weeks without delivery). The stock drains to zero, recorded consumption is cut to the available stock and is zero while `quantity_on_hand` is zero. Additional stock-outs arise naturally for lumpy items with long lead times. The difference between true demand and recorded consumption is the censored demand |
| Stock balance | `quantity_on_hand` is the closing balance of the week and satisfies `closing(t) = closing(t−1) + receipts(t) − consumption(t)` for every item and week; there are no write-offs, returns or expiries in the synthetic data |
| Period | Weekly periods ending on the Monday given by `--end` (default `2026-10-12`, the last complete week before the first pre-defense); `--weeks` periods back from there |

### 10.3 Generation and reproducibility (NFR-05)

```
python forecasting/data/generate_synthetic.py --items 30 --weeks 156 --seed 42 --out <dir>
```

| Argument | Default | Meaning |
|---|---|---|
| `--items` | 30 | Number of items |
| `--weeks` | 156 | Number of weekly periods (3 years); must be at least 8, otherwise the generator stops with `error: --weeks must be at least 8` and exit code 2 |
| `--seed` | 42 | Seed of the random generator; the same arguments reproduce byte-identical files |
| `--out` | `synthetic` | Output directory |
| `--end` | `2026-10-12` | `period_start` of the last week (must be a Monday) |
| `--write-truth` | off | Also write `true_demand.csv` (`item_code,period_start,demand,quantity,is_stock_out`) with the uncensored demand, for experiments on censored-demand handling |
| `--omit-zero-rows` | off | Omit zero-consumption rows from `consumption.csv` to mimic movement-only exports (tests the filling rules of section 6) |

Outputs: the four import files of section 3, `items.csv` (section 3.5) and `dataset.json` with the parameters, the period, row counts and, per item, the generation parameters (class, mean weekly demand, occurrence probability, seasonality, trend, lead time, delayed-delivery episodes, spike weeks) and observed statistics (ADI, CV², observed class, zero share, stock-out weeks and episodes, censored demand units). The generator needs Python 3.12 with pandas and numpy only.

### 10.4 Sample dataset in the repository

`forecasting/data/sample/` holds the files generated with `--items 20 --weeks 104 --seed 42` (about 210 KB in total; the generator prints the exact size); it is the fixture for backend and forecasting tests and for the first experiments.

| Statistic | Value |
|---|---|
| Items / weeks | 20 / 104 (2024-10-21 … 2026-10-12) |
| Rows | consumption 2,080; stock 2,080; receipts 330; planned receipts 18 |
| Demand classes (generation truth) | smooth 6, intermittent 5, erratic 3, lumpy 6 |
| Items with seasonality / trend / a demand spike | 5 / 8 / 5 |
| Items with delayed-delivery episodes | 9 |
| Stock-out weeks | 78 of 2,080 item-weeks (3.8 %) in 14 items; 6 items never out of stock; 49 weeks with zero recorded consumption and 29 partial weeks |
| Censored demand | 3,050 units of true demand not recorded (2.5 % of the 121,641 units consumed) |
| Zero-consumption weeks | 854 (41 %), mostly in intermittent and lumpy items |
| Suppliers | SK-Pharmacy 14 items, Distributor A 4, Distributor B 2; lead times 7–56 days |
| Medicine groups | Antibacterials 6, Analgesics and antipyretics 4, Infusion solutions 3, Gastrointestinal 3, Antidiabetics 2, Anticoagulants 2 |

### 10.5 Limitations

- Demand sizes and their variability are chosen by the team, not estimated from a real pharmacy; group-level differences in real data may be larger or smaller.
- The replenishment policy is simplified (one supplier per item, weekly review, no minimum order quantities, no expiry, no write-offs, no transfers between departments).
- Seasonality is a single annual cosine; real data may show holiday effects, procurement cycles of the central distributor and structural breaks.
- Delayed-delivery episodes are the only mechanism that creates long stock-outs; real stock-outs also come from budget limits and tender failures that affect many items at once.
- The sample is small (20 items); performance measurements (NFR-01, NFR-02) use a dataset generated with `--items 1000 --weeks 156`.

## 11. Status of real-data access

| Aspect | Status as of 2026-10-18 |
|---|---|
| Request | Access to historical consumption, stock and receipt data of a partner healthcare organization has been requested through the supervisor. The request is pending; no date has been promised. Tracked as project risk in `docs/project-management/risks.md` |
| Expected form | Exports from the organization's accounting system or spreadsheets, aggregated per item and week or per item and day; a mapping of export columns to the formats of section 3 will be written when the structure is known |
| Minimum useful history | At least 2 years of weekly data (104 weeks) per item to estimate annual seasonality and keep a hold-out period of 12 weeks; stock balances at least monthly, weekly preferred; receipts with dates |
| Privacy | Only item-level aggregates are accepted (NFR-04). Any export that contains patient, prescription or employee columns is reduced to the agreed columns before it enters the repository or the system; such files are never committed |
| Use of the synthetic dataset afterwards | The synthetic sample stays in the repository as the test fixture; experiments are repeated on real data and both results are reported, each labelled with its data source |

## 12. Open questions

| ID | Question | Affects | Resolution path |
|---|---|---|---|
| Q-1 | Should unknown item codes in `consumption.csv` create catalogue entries (import option `create_items`) or always be rejected? Default: rejected (same as Q2 in `docs/requirements.md`) | V-05, FR-02, FR-03 | Stakeholder interview; backend decision |
| Q-2 | Should unknown supplier names in receipts be created automatically (proposed here, V-11) or rejected (the current text of `docs/architecture/api-contract.md`, error code `unknown_supplier`)? Until decided, the API contract stands and the backend rejects unknown suppliers | V-11, FR-04, API contract | Backend decision; then update V-11 or the API contract so that both say the same |
| Q-3 | Should `items.csv` become a fifth import type for the catalogue and lead times? | section 3.5, FR-03, FR-04 | Decide with the API contract |
| Q-4 | Re-import of a period already stored is decided: replace (V-15, `INSERT ... ON CONFLICT DO UPDATE`). Still open: are corrections exported as the full period or as changed rows only? With changed rows only, rows of the period that are absent from the new file keep their old values | V-15 | Confirm with pharmacy staff when the real export format is known (section 11) |
| Q-5 | Daily exports: is the `granularity=daily` option needed, or will the organization export weekly aggregates? | V-07 | Depends on the real-data export (section 11) |

## 13. Change log

| Date | Version | Author | Change |
|---|---|---|---|
| 2026-10-18 | 0.1 | Evelina Penkova | Initial version: conventions, import formats, entity mapping, validation rules, missing weeks, stock-out flag, data-quality summary, forecasting input frame, synthetic dataset, real-data status |
| 2026-10-20 | 0.2 | Evelina Penkova | Aligned with `docs/requirements.md`, `docs/architecture/api-contract.md` and the forecasting package (PHA2-16): daily exports are aggregated before import and V-07 narrowed (`granularity=daily` kept only as Q-5); V-02 compares header names exactly and case-sensitively; V-15 replace-on-reimport decided (`INSERT ... ON CONFLICT DO UPDATE`) and Q-4 narrowed; outlier rule per FR-18 (`outlier_factor` × median non-zero quantity, at least 8 non-zero weeks); gaps between imports filled with zero, flagged and counted (`is_filled`, `n_filled_weeks`) instead of missing values; leading-zero trimming described as planned without a configuration key; censoring methods per FQ-10 (`censoring_method`: `exclude` implemented in the experiment runner, `impute` planned); schema and validation modules marked as implemented; `--weeks` minimum documented; generator test `forecasting/tests/test_generate_synthetic.py` added |
