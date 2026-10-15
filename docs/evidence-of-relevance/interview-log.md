# Interview log and evidence register

`PHA2-7` · Evidence of relevance · Last updated: 2026-10-15 · Author: Birkhanym Kazhymukhamet

This log records every discussion, observation and data analysis carried out for the PharmaStock project and keeps an explicit separation between **verified findings** (stated by a representative of the relevant role, observed directly, or measured in data) and **assumptions** (what the team currently believes but has not checked). Planned discussions are listed in [stakeholders.md](./stakeholders.md); the questions are in the [interview guide](./interview-guide.md).

## 1. Status

| Item | Value (2026-10-14) |
|------|--------------------|
| Discussions completed | 0 of 5 planned (D-1 to D-5) |
| Discussions scheduled | 0; D-1 and D-2 to be scheduled by 2026-10-24 |
| Process observations completed | 0 (planned together with D-2) |
| Real data analysed | none yet; access requested, see section 4 |
| Verified findings | 0 |
| Assumptions awaiting verification | 16 (section 3) |

Until the first discussions are held, **all statements about the domain in the requirements and the proposal are assumptions** and are marked as such below. No interview content has been invented to fill this log.

## 2. Discussion log

One row per discussion; the full mapping of assumptions to discussions is in section 3.2. Names and organization names are not recorded (see consent note in the [interview guide](./interview-guide.md#7-consent-and-personal-data)).

| ID | Date | Role | Organization type | Format | Interviewer / note-taker | Consent (notes / audio) | Key findings (block.question → finding) | Classification | Primary assumptions | Follow-up |
|----|------|------|-------------------|--------|--------------------------|-------------------------|-------------------------------------------|----------------|---------------------|-----------|
| D-1 | to be scheduled | Head of hospital pharmacy | Multi-profile hospital | Interview, 50–60 min | B. Kazhymukhamet / E. Penkova | — | — | — | A-01–A-07, A-10, A-11 | — |
| D-2 | to be scheduled | Pharmacist | Polyclinic or hospital pharmacy | Interview + workflow observation | B. Kazhymukhamet / A. Bakhytov | — | — | — | A-01, A-06, A-08, A-13, A-14 | — |
| D-3 | to be scheduled | Procurement and supply specialist | Hospital | Interview, 35–45 min | B. Kazhymukhamet / E. Penkova | — | — | — | A-03, A-09, A-11 | — |
| D-4 | to be scheduled | IT administrator | Same organization as D-1 or D-2 | Interview, 20–30 min | A. Bakhytov / B. Kazhymukhamet | — | — | — | A-01, A-12, A-15, A-16 | — |
| D-5 | to be scheduled | Head of clinical department | Hospital | Interview, 20 min | B. Kazhymukhamet / A. Bakhytov | — | — | — | A-10 | — |

Row format for a completed discussion (example of the expected form, not a record):

```text
| D-n | YYYY-MM-DD | <role> | <organization type> | <format> | <interviewer> / <note-taker> | yes / no | B1 → <finding>; C6 → <finding> | verified finding | FR-xx, A-xx confirmed | <next step> |
```

Each key finding is written as a short factual statement in the participant's own terms, followed by the block and question number from the guide. Opinions and wishes ("it would be nice to...") are recorded separately from facts ("we export data monthly").

## 3. Verified findings vs assumptions

### 3.1 Verified findings

| ID | Finding | Source (discussion / observation / data) | Date | Affects |
|----|---------|------------------------------------------|------|---------|
| — | No verified findings yet. The first entries are expected after D-1 and D-2. | — | — | — |

### 3.2 Assumptions to be verified

Each assumption states where it came from, how it will be checked, and which requirement or design decision depends on it. Status values: `ASSUMPTION` (not yet checked), `CONFIRMED` (moved to 3.1 with source), `CONTRADICTED` (change proposal opened), `PARTIALLY CONFIRMED` (with a note).

| ID | Assumption | Origin | Planned verification | Depends on it | Status (2026-10-14) |
|----|------------|--------|----------------------|---------------|---------------------|
| A-01 | Pharmacy stock in healthcare organizations is recorded mostly in an accounting system (1C-type) and in spreadsheets; item-level exports to XLSX or CSV are possible but produced manually. | Proposal, team's prior knowledge of accounting practice | D-1 (B1, D1), D-2, D-4 | FR-01, FR-02, import formats in data specification; decision to import files rather than integrate in real time | ASSUMPTION |
| A-02 | Consumption of most items is intermittent: long runs of zero weekly demand with occasional spikes; a minority of items are consumed every week. | Proposal; literature on hospital pharmacy demand | D-1 (A2, F2), analysis of real exports when available | Choice of Croston/SBA baselines and of MAE/WAPE instead of MAPE; error analysis per medicine group | ASSUMPTION |
| A-03 | Lead times are long because most items come through centralised procurement (SK-Pharmacy, guaranteed volume of free medical care) with an annual plan, while own purchases cover the rest with shorter but variable lead times. | Proposal; public information on the single-distributor model | D-1 (E1, E2), D-3 (block E), desk research of public procurement documents | Risk level "High" defined by lead time; `item_supplier.lead_time_days`; FR-04 | ASSUMPTION |
| A-04 | Shortages are discovered late, usually when stock is already at or near zero, because detection is manual (someone notices while issuing or during an inventory count). | Proposal | D-1 (C1, C2), D-2 (C1–C4), D-5 (C1) | Problem statement; FR-08, FR-09, FR-12; value of an early-warning signal | ASSUMPTION |
| A-05 | At the same time some items are overstocked and expire before use, so the problem is misallocation, not only under-ordering. | Proposal | D-1 (C5), D-3 | Expected outcomes; future replenishment calculations (Feb 2027 milestone) | ASSUMPTION |
| A-06 | A weekly time step is sufficient for ordering decisions; daily granularity is not needed and monthly is too coarse. | Initial design decision | D-1 (B2, F4), D-2 (B2), D-1/D-2 (H7) | Weekly `period_start` in all data entities; `forecast_run.horizon_weeks`; seasonal period 52 | ASSUMPTION (open for revision) |
| A-07 | A 12-week forecast horizon covers the decision window for own purchases and gives early enough warning for adjustments to centralised supply. | Initial design decision | D-1 (F4), D-3 (E2, F4) | Default horizon; risk level "Medium" defined by the horizon | ASSUMPTION (open for revision) |
| A-08 | Stock-out periods are not recorded explicitly, but weekly stock levels are available, so weeks with zero stock can be derived and flagged as censored demand. | Team's reasoning about typical exports | D-2 (C6, D2), analysis of real exports | FR-17, `stock_snapshot.is_stock_out`; forecasting data validation | ASSUMPTION |
| A-09 | Expected deliveries (date and quantity) are known in advance at least for centralised supply, so planned receipts can be entered and used in the projected-stock calculation. | Team's reasoning | D-3 (D5, E4), D-1 (E4) | FR-10, `planned_receipt` entity, risk logic | ASSUMPTION |
| A-10 | The head of pharmacy and pharmacists are the primary users; heads of clinical departments need read-only access; three roles (administrator, pharmacist, viewer) are sufficient. | Proposal | D-1 (A3, H3), D-5 (H1, H3) | FR-14, `app_user.role`, UX scenarios | ASSUMPTION |
| A-11 | Safety-stock or minimum-stock rules exist but are informal and item-specific; they are set by the pharmacy rather than imposed centrally. | Team's reasoning | D-1 (F1), D-3 (F1) | FR-11, `threshold_config`, safety stock in the risk formula | ASSUMPTION |
| A-12 | Item-level totals per period are enough for forecasting and risk calculation; no patient-level or prescription-level data is needed, and organizations can share such totals without a data-protection obstacle. | Proposal, NFR-04 | D-4 (data export questions), D-1 (D1), response to the data request | NFR-04; feasibility of the data request | ASSUMPTION |
| A-13 | At least two to three years of weekly consumption history per item are available in the accounting system. | Team's reasoning | D-2 (D3), D-4, analysis of real exports | Seasonal baselines (need ≥ 2 seasons); time-based split; NFR-01 sizing | ASSUMPTION |
| A-14 | Item codes are reasonably stable, but renaming and re-coding happen (packaging or supplier changes), so the import must detect unknown items and the catalogue must support an active flag. | Team's reasoning | D-2 (D4), D-1 (D4), analysis of real exports | FR-02, FR-03, `medicine_item.is_active`, FR-18 | ASSUMPTION |
| A-15 | Users work on desktop computers in a current browser; an English interface is acceptable for the prototype, with Russian localisation needed for real adoption. | Team's reasoning | D-1 (H6), D-4 | NFR-09, NFR-10 | ASSUMPTION |
| A-16 | The organization can run the prototype on an internal server or virtual machine (Linux, Docker), and sending data to an external cloud service would not be acceptable. | Team's reasoning | D-4, D-1 (H5, H6) | NFR-07, deployment design, scope exclusion of multi-organization SaaS | ASSUMPTION |

### 3.3 How requirements are linked to evidence

| Requirement group | Current evidence basis | Target after discussions |
|-------------------|------------------------|--------------------------|
| Import and validation (FR-01, FR-02, FR-17, FR-18) | A-01, A-08, A-14 | Confirmed export formats and known data-quality problems from D-2 and D-4, plus statistics from real exports |
| Catalogue, suppliers, lead times (FR-03, FR-04, FR-10) | A-03, A-09, A-14 | Lead-time ranges and delivery practice from D-3 |
| Forecasting and comparison (FR-06, FR-07, FR-16; weekly step, 12-week horizon) | A-02, A-06, A-07, A-13 | Decision window and preferred presentation from D-1; intermittency profile from data |
| Risk calculation and notifications (FR-08, FR-09, FR-11, FR-12) | A-04, A-05, A-11 | Current detection practice and decision rules from D-1, D-3, D-5 |
| Roles, security, deployment (FR-14, FR-15, NFR-03, NFR-04, NFR-07) | A-10, A-12, A-15, A-16 | Organizational constraints from D-4 |

When an assumption is confirmed or contradicted, the corresponding rows in [docs/requirements.md](../requirements.md) receive a reference to the log entry (for example "Evidence: D-1, C6") in the same pull request.

## 4. Analysis of available data

### 4.1 Real data

Access to anonymised, item-level consumption, stock and receipt exports is being requested from a partner healthcare organization through the team's contacts. The request specifies the formats described in [docs/data/data-specification.md](../data/data-specification.md): weekly consumption per item, weekly stock on hand per item, receipts with date, quantity and supplier, and planned deliveries where available. No patient data or personal data is requested.

| Item | Status (2026-10-14) |
|------|---------------------|
| Request for anonymised exports | in progress (October 2026); answer pending |
| Expected form of data | XLSX or CSV exports from the accounting system, possibly monthly rather than weekly (to be confirmed in D-2 and D-4) |
| Risk | Delay or refusal is a project risk tracked in [docs/project-management/risks.md](../project-management/risks.md); the mitigation is the documented synthetic dataset described below |
| Responsible | Evelina Penkova (data request and analysis), Birkhanym Kazhymukhamet (contact with the organization) |

When real data arrive, the following analysis is planned and its results will be recorded here as verified findings:

1. coverage: number of items, history length per item, share of items with at least two full years of history;
2. intermittency profile: share of zero weeks per item, average demand interval and coefficient of variation of non-zero demand, to classify items (smooth, intermittent, erratic, lumpy);
3. stock-out weeks: share of weeks with zero stock per item, to quantify how much demand is censored (A-08, FR-17);
4. data quality: missing periods, negative or corrected quantities, duplicate periods, unknown or re-coded items (FR-02, FR-18, A-14);
5. receipts and lead times: distribution of intervals between recorded receipts and, where planned deliveries exist, between expected and actual dates (A-03, A-09).

### 4.2 Synthetic dataset used meanwhile

Until real data are available, development and the first experiments use a documented synthetic dataset produced by the script `forecasting/data/generate_synthetic.py` (sample files in `forecasting/data/sample/`, parameters documented in [docs/data/data-specification.md](../data/data-specification.md)). The script encodes the assumptions above explicitly so that they can be replaced one by one as findings arrive:

| Property of the synthetic data | Assumption it encodes | Replaced by |
|--------------------------------|-----------------------|-------------|
| Weekly periods, `period_start` is the Monday of the week | A-06 | confirmed granularity from D-1, D-2 |
| Mix of smooth, intermittent, erratic and lumpy items; the share of zero weeks per item is drawn from the seeded generator and recorded in dataset.json | A-02 | intermittency profile from real exports |
| Annual seasonality on a subset of items | A-02, F2 answers | seasonality observed in real data |
| Stock-out weeks injected as zero `quantity_on_hand` in `stock.csv`, flagged on import as `is_stock_out` | A-08 | real share of stock-out weeks |
| Lead times per supplier spanning short own purchases and long centralised supply | A-03 | lead-time ranges from D-3 |
| Planned receipts with occasional delay | A-09 | delivery practice from D-3 |

The synthetic dataset is suitable for checking that the pipeline, metrics and risk logic work and for comparing baselines under controlled conditions. It is **not** evidence about the domain, and no conclusion about real consumption patterns will be drawn from it; this limitation will be stated in the thesis and in the evaluation plan.

## 5. Process observations

| ID | Date | Process observed | Organization type | Observer | Key observations | Classification |
|----|------|------------------|-------------------|----------|------------------|----------------|
| O-1 | planned with D-2 | Recording of receipts, issues and stock check in the pharmacy | Polyclinic or hospital pharmacy | B. Kazhymukhamet | — | — |

Observation is subject to the organization's permission and will be recorded only as a description of steps, tools and approximate time; no documents or screens containing personal data will be copied or photographed.

## 6. Change log

| Date | Change | Author |
|------|--------|--------|
| 2026-10-14 | Log created: discussion plan, assumptions A-01 to A-16, data-availability status, observation plan. No discussions held yet. | Birkhanym Kazhymukhamet |
