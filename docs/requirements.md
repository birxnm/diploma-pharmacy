# PharmaStock — Requirements Specification

Task: PHA2-11 · Last updated: 2026-10-16 · Status: draft v0.1 · Author: Birkhanym Kazhymukhamet

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and non-functional requirements of **PharmaStock**, the smart supply chain analytics system developed as the diploma project "Development of smart supply chain analytics system for forecasting pharmaceutical inventory and preventing medicine shortages in healthcare organizations" (Astana IT University, School of Software Engineering, group SE-2414, academic year 2026–2027).

The document is the agreed reference for the whole team: the backend, the forecasting module, the web interface, the database schema and the verification plan are derived from the requirement IDs listed here. Requirement IDs (FR-xx, NFR-xx) are fixed and are reused verbatim in task descriptions, pull requests, test names and the thesis text.

### 1.2 Scope of the system

PharmaStock is a prototype that:

- imports consumption, stock and receipt data exported from the accounting system or spreadsheets of a healthcare organization;
- forecasts weekly consumption per medicine item for a configurable horizon (initial decision: weekly step, 12-week horizon);
- turns the forecast, current stock, planned receipts and lead time into a shortage-risk signal per item;
- presents a prioritised risk list, dashboards and item pages to pharmacy staff.

The full scope boundary (in and out of scope) is given in section 5.4. The problem statement, aim and objectives are in `docs/proposal.md`.

### 1.3 How to read this document

| Element | Meaning |
|---|---|
| FR-xx | Functional requirement |
| NFR-xx | Non-functional requirement |
| Priority | MoSCoW: **Must** (required for the prototype to be accepted), **Should** (important, planned for the prototype), **Could** (desirable, implemented if time allows), **Won't** (explicitly excluded in this project) |
| Source | Where the requirement comes from: **supervisor plan** (approved plan and justification letter of 9 October 2026), **assumption** (team decision based on the domain analysis, open for revision), **interview-to-verify** (to be confirmed with pharmacy staff during stakeholder interviews, see `docs/evidence-of-relevance/interview-guide.md`) |
| AC | Acceptance criterion, used by the verification plan (`docs/verification-and-evaluation-plan.md`) |

### 1.4 Related documents

| Document | Path |
|---|---|
| Project proposal | `docs/proposal.md` |
| Stakeholder description and interview guide | `docs/evidence-of-relevance/` |
| User scenarios and use cases | `docs/ux/user-scenarios.md`, `docs/ux/use-cases.md` |
| Architecture, API contract, database schema | `docs/architecture/` |
| Data specification (import formats, synthetic dataset) | `docs/data/data-specification.md` |
| Verification and evaluation plan | `docs/verification-and-evaluation-plan.md` |
| Task register | `docs/project-management/task-register.md`, [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b) |

---

## 2. Stakeholders and user roles

### 2.1 Stakeholders

| Stakeholder | Interest in the system | Involvement in the project |
|---|---|---|
| Head of hospital pharmacy / pharmacist | Knows which items will run out and when; plans requests to the distributor and own purchases earlier; reduces overstock and expiry write-offs | Primary user; source of requirements and user testing (planned interviews) |
| Procurement and supply specialist | Uses the risk list and expected stock-out dates to prioritise orders; records planned deliveries | Secondary user; interview-to-verify |
| Heads of clinical departments | See the availability outlook for the medicines their department depends on | View-only users; interview-to-verify |
| System administrator (IT staff of the organization) | Installs and maintains the system, manages users and roles, reviews the audit log | User; deployment feedback |
| Hospital management | Reporting on shortage risk and stock health; justification for procurement decisions | Indirect; consumer of exported reports |
| Partner healthcare organization | Provides historical consumption, stock and receipt exports under an agreement | Data provider; access is being requested and is tracked as a project risk (`docs/project-management/risks.md`) |
| Supervisor (Kuralay Makhmetova) | Methodological guidance, approval of plan and evaluation methodology | Weekly meetings; review of deliverables |
| Project team (Birkhanym Kazhymukhamet, Abzal Bakhytov, Evelina Penkova) | Delivery of the prototype, thesis and article | Owners of this document |

Patients are **not** stakeholders of the system: no patient is a user and no patient data is processed (NFR-04).

### 2.2 User roles

The system has three application roles (FR-14). The mapping to real positions in a healthcare organization is given below; one person can hold only one role.

| Role | Typical holder | What the role can do |
|---|---|---|
| **administrator** | System administrator | Everything a pharmacist can do; manage users and roles; configure thresholds and safety-stock parameters; view the audit log |
| **pharmacist** | Head of hospital pharmacy, pharmacist, procurement and supply specialist | Import data; maintain the catalogue, suppliers and planned receipts; run forecasts; view and export forecasts, risk lists and reports; receive notifications |
| **viewer** | Head of clinical department, management | View dashboards, item pages, forecasts and risk lists; export reports; no modifying actions |

The detailed permission matrix is part of the acceptance criteria of FR-14 (section 6).

### 2.3 Primary user scenarios (summary)

The detailed scenarios are in `docs/ux/user-scenarios.md`. The requirements below cover the following main flows:

1. **Weekly data update** — the pharmacist exports the latest consumption and stock data and imports it; the system validates the file and shows a data-quality summary.
2. **Forecast and risk review** — the pharmacist runs the forecast, opens the risk list, reviews High-risk items and their expected stock-out dates, and records planned deliveries that change the picture.
3. **Item investigation** — a user opens an item page to see stock history, consumption history, the forecast with its interval and the model that produced it.
4. **Configuration and administration** — the administrator manages users, adjusts thresholds and checks the audit log.
5. **Model evaluation** — the team compares forecasting models against baselines on a hold-out period and documents the results.

---

## 3. Functional requirements

| ID | Requirement | Priority | Source |
|---|---|---|---|
| FR-01 | Import consumption, stock and receipt data from CSV/XLSX files | Must | supervisor plan |
| FR-02 | Validate imported data and report errors: missing columns, negative quantities, unknown items, duplicate periods | Must | supervisor plan |
| FR-03 | Maintain the medicine catalogue: code, name, unit, group, active flag | Must | assumption |
| FR-04 | Maintain suppliers and lead times per item | Should | interview-to-verify |
| FR-05 | View current stock and consumption history per item as table and chart | Must | assumption |
| FR-06 | Run a forecast for all or selected items for a configurable horizon | Must | supervisor plan |
| FR-07 | View the forecast per item together with history, point forecast, interval and model information | Must | supervisor plan |
| FR-08 | Calculate shortage risk per item from forecast, current stock, planned receipts and lead time | Must | supervisor plan |
| FR-09 | Show a prioritised list of items at risk with risk level and expected stock-out date | Must | supervisor plan |
| FR-10 | Record planned deliveries (expected receipts) | Should | interview-to-verify |
| FR-11 | Configure risk thresholds and safety-stock parameters | Should | interview-to-verify |
| FR-12 | Generate in-app notifications for high-risk items | Should | supervisor plan |
| FR-13 | Export forecast and risk reports to CSV/XLSX | Should | interview-to-verify |
| FR-14 | Authenticate users and manage roles: administrator, pharmacist, viewer | Must | supervisor plan |
| FR-15 | Keep an audit log of imports, forecast runs and configuration changes | Should | supervisor plan |
| FR-16 | Compare forecasting models against baselines on a hold-out period and show MAE and WAPE | Should | supervisor plan |
| FR-17 | Flag stock-out periods so that zero consumption during a stock-out is treated as censored demand | Must | assumption |
| FR-18 | Show a data-quality summary per import: coverage, gaps, outliers | Should | assumption |

Notes on sources:

- *supervisor plan* — the requirement follows directly from the aim, objectives and responsibilities in the plan approved by the supervisor (justification letter of 9 October 2026) and from the proposal.
- *assumption* — the requirement is a team decision derived from the domain analysis (intermittent demand, long lead times, censored demand during stock-outs). It stays in the specification unless an interview contradicts it.
- *interview-to-verify* — the requirement is expected to be useful but its details (for example, whether lead times are maintained per item or per supplier, which export formats are needed) must be confirmed with pharmacy staff. Until then it is treated as planned.

---

## 4. Non-functional requirements

| ID | Requirement | Priority | Category |
|---|---|---|---|
| NFR-01 | A forecast run for 1,000 items with 3 years of weekly history completes within 5 minutes on a 4 vCPU / 8 GB server | Should | Performance |
| NFR-02 | Typical pages respond within 2 seconds with up to 5,000 items | Should | Performance |
| NFR-03 | Role-based access control; passwords stored hashed; HTTPS in deployment | Must | Security |
| NFR-04 | No patient personal data is stored or processed | Must | Privacy / compliance |
| NFR-05 | Forecast experiments are reproducible: fixed seeds, versioned configurations, saved results | Must | Reproducibility |
| NFR-06 | The forecasting module rejects malformed input with a clear error instead of producing a wrong forecast | Must | Reliability |
| NFR-07 | Deployable with Docker Compose on Linux with documented setup | Should | Deployability |
| NFR-08 | Automated tests for backend and forecasting run in CI on every pull request | Must | Maintainability |
| NFR-09 | UI works in current Chrome, Firefox and Edge on desktop, responsive down to 1280 px | Should | Usability / compatibility |
| NFR-10 | Interface in English first; Russian localisation planned | Could | Usability |

Non-functional requirements are verified according to `docs/verification-and-evaluation-plan.md` (performance measurements on the synthetic dataset, code review for NFR-03/NFR-04, CI configuration for NFR-08, browser checks for NFR-09).

---

## 5. Constraints

### 5.1 Project constraints

- The system is a diploma project of a three-person team with fixed responsibilities (`docs/project-management/responsibilities.md`); development runs from September 2026 to June 2027 with the milestones in `docs/project-management/plan-and-milestones.md`. First pre-defense materials are due 24 October 2026.
- Individual contribution is tracked per task ([Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b), link will be added when the instance is confirmed), per commit and per demo; every requirement therefore has a single owner for its acceptance criteria.
- The result is a prototype, not a certified medical or accounting product. It does not replace the organization's accounting system; it works on exports from it.

### 5.2 Technical constraints

- Technology stack is decided (justification in `docs/technology-comparison.md`): Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, PostgreSQL 16; forecasting with pandas, numpy, scikit-learn, statsforecast and LightGBM; frontend with Vue 3, Vite, TypeScript, Vue Router, Pinia and Chart.js; Docker Compose for PostgreSQL; GitHub Actions CI; pytest and Vitest.
- The forecasting module is an in-process Python package called by the backend (`forecasting.api.forecast_items(history, horizon, config) -> ForecastResult`); it is not a separate service in this project.
- Data enters the system only through file import (CSV/XLSX). There is no real-time integration with 1C, with the distributor SK-Pharmacy or with national health information systems; this is future work.
- The web interface targets desktop browsers (NFR-09). There is no mobile application.
- The system is single-tenant: one deployment serves one healthcare organization.

### 5.3 Data and privacy constraints

- Access to real historical data from a partner healthcare organization is being requested and is a project risk. Until real data are available, development and experiments use a documented synthetic dataset (`docs/data/data-specification.md`, `forecasting/data/generate_synthetic.py`). All results reported on synthetic data are labelled as such.
- Only item-level aggregated data (consumption per item per week, stock levels, receipts) are stored. No patient-level, prescription-level or personal data are imported, stored or processed (NFR-04). Import files that contain such columns must be reduced to the agreed formats before import.
- Zero consumption during a stock-out is censored demand: it must be flagged (FR-17) and must not be learned as zero demand by the forecasting models.
- The time step is one week; `period_start` is the Monday of the week. Daily data in exports must be aggregated to weeks before import (see `docs/data/data-specification.md`); rows whose `period_start` is not a Monday are rejected.

### 5.4 Scope boundary

| In scope | Out of scope (this project) |
|---|---|
| Import of consumption / stock / receipt data from CSV/XLSX exports | Ordering and procurement execution (purchase orders, contracts) |
| Medicine catalogue; suppliers and lead times | Electronic prescriptions |
| Weekly consumption forecast per item for a configurable horizon | Real-time integration with national systems and 1C (future work) |
| Shortage-risk calculation; prioritised risk list; in-app notifications | Mobile application |
| Dashboards and item pages; thresholds and safety-stock configuration | Patient data of any kind |
| Users and roles; audit log; export of reports | Multi-organization SaaS |
| Model comparison on hold-out data | |

---

## 6. Acceptance criteria

Acceptance criteria are written for the **Must** functional requirements in this version. Criteria for the Should/Could requirements and for the non-functional requirements are **to be added** by the owners named in the table below.

| Requirement | Owner of criteria | Status |
|---|---|---|
| FR-01, FR-02, FR-03, FR-08, FR-09, FR-14 | Abzal Bakhytov | present (draft) |
| FR-05 | Birkhanym Kazhymukhamet | present (draft) |
| FR-06, FR-07, FR-17 | Evelina Penkova | present (draft) |
| FR-04, FR-10, FR-11, FR-12, FR-13, FR-15 | Abzal Bakhytov / Birkhanym Kazhymukhamet | to be added |
| FR-16, FR-18 | Evelina Penkova | to be added |
| NFR-01 … NFR-10 | per category owner | to be added |

### 6.1 FR-01 — Import consumption, stock and receipt data from CSV/XLSX files

- AC-01.1 A pharmacist or administrator can upload a file of type `consumption`, `stock`, `receipts` or `planned_receipts` in CSV or XLSX format through the web interface and through `POST /api/v1/imports`. The accepted column sets are defined in `docs/data/data-specification.md`.
- AC-01.2 Every upload creates an `import_batch` record with file name, source type, timestamp, user and final status; imported rows reference the batch so that an import can be traced and reviewed later.
- AC-01.3 A file that fails validation (FR-02) stores no data rows; the batch is kept with status `failed` and the list of errors.
- AC-01.4 After a successful import the user sees the number of rows imported, the items affected and the period covered (basis for FR-18).

### 6.2 FR-02 — Validate imported data and report errors

- AC-02.1 A file with a missing required column is rejected and the message names the missing column(s).
- AC-02.2 Rows with a negative quantity, an unknown item code or a duplicate (item, period) pair are reported with the row number, the column and the offending value.
- AC-02.3 The validation report is shown in the web interface after upload and is available through `GET /api/v1/imports/{id}`.
- AC-02.4 Validation is all-or-nothing per file: if any error is found, no rows of that file are stored.

### 6.3 FR-03 — Maintain the medicine catalogue

- AC-03.1 A pharmacist or administrator can create and edit items with code, name, unit, group and active flag; the item code is unique.
- AC-03.2 Deactivating an item keeps its history and forecasts but excludes it from new forecast runs and from the risk list by default.
- AC-03.3 The item list can be searched by code and name and filtered by group and active flag.
- AC-03.4 A viewer can see the catalogue but cannot modify it.

### 6.4 FR-05 — View current stock and consumption history per item

- AC-05.1 The item page shows the current stock (latest stock snapshot with its date) and the weekly consumption history as a table and as a line chart.
- AC-05.2 Weeks flagged as stock-out (FR-17) are visually marked in the chart and in the table.
- AC-05.3 The user can choose the history range (last 26 weeks, last 52 weeks, all) and the chart updates without reloading the page.
- AC-05.4 The page is usable at 1280 px width (NFR-09) and loads within 2 seconds for an item with 3 years of history (NFR-02).

### 6.5 FR-06 — Run a forecast for all or selected items

- AC-06.1 A pharmacist or administrator can start a forecast run for all active items or for a selected subset, choosing the horizon in weeks (default 12).
- AC-06.2 The run is recorded as a `forecast_run` with status (`queued`, `running`, `completed`, `failed`), model name and configuration, and its progress is visible in the interface.
- AC-06.3 A completed run contains one forecast row per item and per week of the horizon.
- AC-06.4 Items with insufficient history are listed in the run summary with a reason; they are not silently skipped.

### 6.6 FR-07 — View the forecast per item

- AC-07.1 The item forecast view shows history and forecast on one chart: the point forecast, the lower and upper bounds of the interval, and a visual boundary between history and forecast.
- AC-07.2 The view shows the model name, the run date, the horizon and a link to the run.
- AC-07.3 The same values are available as a table and through `GET /api/v1/items/{id}/forecast`.

### 6.7 FR-08 — Calculate shortage risk per item

- AC-08.1 For every item of a completed forecast run the system computes the projected stock per week as `current stock + planned receipts due by that week − cumulative forecast up to that week`.
- AC-08.2 The expected stock-out date is the first week in which the projected stock is less than or equal to the safety stock of the item.
- AC-08.3 The risk level is **High** if the stock-out is expected within the item's lead time, **Medium** if within the forecast horizon, **Low** otherwise.
- AC-08.4 The result is stored as a `risk_assessment` with the risk level, the expected stock-out date and the projected stock series.

### 6.8 FR-09 — Show a prioritised list of items at risk

- AC-09.1 The risk list is ordered High → Medium → Low and, within a level, by expected stock-out date ascending.
- AC-09.2 The list can be filtered by risk level (`GET /api/v1/risks?level=high|medium|low`) and shows item code, name, group, current stock, lead time, expected stock-out date and risk level.
- AC-09.3 Every row links to the item page with its forecast.

### 6.9 FR-14 — Authenticate users and manage roles

- AC-14.1 Users log in with e-mail and password (`POST /api/v1/auth/login`); failed logins return a generic error without revealing whether the e-mail exists.
- AC-14.2 Every API endpoint and every page enforces the permission matrix below; a forbidden action returns HTTP 403.
- AC-14.3 Only an administrator can create users, assign roles and deactivate users; passwords are stored hashed (NFR-03) and are never returned by the API.

Permission matrix (draft, to be confirmed with the interviews):

| Action | viewer | pharmacist | administrator |
|---|---|---|---|
| View dashboards, items, history, forecasts, risk list | yes | yes | yes |
| Export reports | yes | yes | yes |
| Import data | – | yes | yes |
| Maintain catalogue, suppliers, planned receipts | – | yes | yes |
| Run forecasts | – | yes | yes |
| Configure thresholds and safety stock | – | yes | yes |
| Manage users and roles | – | – | yes |
| View audit log | – | – | yes |

### 6.10 FR-17 — Flag stock-out periods (censored demand)

- AC-17.1 A week whose stock snapshot shows zero quantity on hand is flagged `is_stock_out` for that item.
- AC-17.2 Zero consumption in a flagged week is passed to the forecasting module as censored, not as an observed zero; the handling method is documented in the forecasting module.
- AC-17.3 Flagged weeks are visible on the item page (FR-05) and counted in the data-quality summary (FR-18).

### 6.11 Acceptance criteria to be added

FR-04, FR-10, FR-11, FR-12, FR-13, FR-15, FR-16, FR-18 and NFR-01 … NFR-10: to be added.

---

## 7. Open questions

| # | Question | Affects | How it will be resolved |
|---|---|---|---|
| Q1 | Are lead times maintained per supplier, per item or per item-supplier pair in practice? | FR-04, FR-08 | Stakeholder interview |
| Q2 | Should unknown item codes in `consumption.csv` (which carries name and unit) create catalogue entries automatically, or always be rejected? | FR-02, FR-03 | Stakeholder interview; default is to reject |
| Q3 | Which report formats and columns are needed for management (CSV, XLSX, both)? | FR-13 | Stakeholder interview |
| Q4 | Is a 12-week horizon with a weekly step adequate for centralised procurement cycles? | FR-06, FR-08 | Stakeholder interview; data analysis |
| Q5 | Will real historical data be available before December 2026? | all experiments | Partner organization; tracked in `docs/project-management/risks.md` |

---

## 8. Revision history

| Date | Version | Author | Change |
|---|---|---|---|
| 2026-10-16 | 0.1 | Birkhanym Kazhymukhamet | Initial version: introduction, stakeholders and roles, FR-01…FR-18, NFR-01…NFR-10, constraints, acceptance criteria for Must requirements |
