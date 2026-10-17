# PharmaStock — Requirements Specification

Task: PHA2-11 · Last updated: 2026-10-17 · Status: draft v0.2 · Authors: Birkhanym Kazhymukhamet (editor), Abzal Bakhytov

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
| Scenario | Acceptance scenario in Given / When / Then form; scenarios are the basis for automated tests and demo scripts |

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
- The time step is one week; `period_start` is the Monday of the week. Daily data in exports must be aggregated to weeks before import (see 5.5.1 and `docs/data/data-specification.md`); rows whose `period_start` is not a Monday are rejected.

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

### 5.5 Data and API constraints

Owner: Abzal Bakhytov. These constraints bind the backend (`backend/`), the import pipeline and the API contract (`docs/architecture/api-contract.md`). The database schema (`docs/architecture/database-schema.md`) uses the entity names of this document.

#### 5.5.1 Import file formats

All import files are CSV (UTF-8, comma separated, header row, decimal point `.`) or XLSX (first sheet, header in the first row, same column names). Dates are ISO 8601 (`YYYY-MM-DD`). `period_start` is always the Monday of the week.

| Source type | File | Columns (exact header) | Target entity |
|---|---|---|---|
| `consumption` | `consumption.csv` | `item_code,item_name,unit,period_start,quantity` | `consumption_record` |
| `stock` | `stock.csv` | `item_code,period_start,quantity_on_hand` | `stock_snapshot` |
| `receipts` | `receipts.csv` | `item_code,received_on,quantity,supplier` | `receipt` |
| `planned_receipts` | `planned_receipts.csv` | `item_code,expected_on,quantity,supplier` | `planned_receipt` |

Rules:

- Column order is not significant; column names are case-sensitive and must match exactly. Additional columns are ignored and listed as a warning in the import summary.
- `quantity` and `quantity_on_hand` are non-negative decimals in the unit of the item; integers are accepted.
- `item_code` must exist in the medicine catalogue (`medicine_item.code`); the import does not create catalogue entries (see open question Q2).
- `supplier` is matched by name to `supplier.name`; an unknown supplier name is an error.
- A (`item_code`, `period_start`) pair must be unique within a `consumption` or `stock` file. Rows of a new import for an (item, period) pair that already exists in the database replace the earlier rows of that pair; the replaced rows are kept linked to their original batch for audit purposes and the replacement is recorded in the import summary.
- Maximum file size is 20 MB; larger files are rejected before parsing.
- Daily rows in a `consumption` file (a `period_start` that is not a Monday) are rejected; aggregation to weeks is the responsibility of the export step and is described in `docs/data/data-specification.md`.

#### 5.5.2 API versioning

- All endpoints are served under the prefix `/api/v1`. The OpenAPI document that FastAPI produces is served under the same prefix (`/api/v1/openapi.json`, interactive documentation at `/api/v1/docs`).
- Within `v1`, only backward-compatible changes are allowed: adding endpoints, adding optional request fields, adding response fields. Removing or renaming fields, changing types or changing semantics requires a new prefix (`/api/v2`), which is not planned for this project.
- The contract is maintained in `docs/architecture/api-contract.md` and must be updated in the same pull request as the code change.
- Authentication uses a bearer token in the `Authorization` header (`Authorization: Bearer <token>`), obtained from `POST /api/v1/auth/login`. All endpoints except `GET /api/v1/health` and `POST /api/v1/auth/login` require authentication.
- List endpoints accept `limit` (default 50, maximum 500) and `offset` (default 0) and return `{"items": [...], "total": <int>, "limit": <int>, "offset": <int>}`.
- Identifiers are integers; timestamps are ISO 8601 in UTC with the `Z` suffix; dates are ISO 8601 calendar dates.

#### 5.5.3 Error format

Every error response has the same JSON body:

```json
{
  "error": {
    "code": "IMPORT_VALIDATION_FAILED",
    "message": "Import rejected: 3 validation errors",
    "details": [
      {"row": 15, "column": "quantity", "value": "-3", "message": "quantity must be >= 0"}
    ]
  }
}
```

- `code` is a stable upper-snake-case identifier that clients may branch on; `message` is a human-readable summary; `details` is an optional list of structured items (for request validation: `field`, `message`; for import validation: `row`, `column`, `value`, `message`).
- Import validation reports at most the first 100 errors in `details` and the total number of errors in the `message`.
- HTTP status codes:

| Status | Used for | Example `code` |
|---|---|---|
| 400 | Malformed request that cannot be parsed (unsupported file type, bad query parameter) | `UNSUPPORTED_FILE_TYPE`, `BAD_REQUEST` |
| 401 | Missing, invalid or expired token; failed login | `UNAUTHENTICATED`, `INVALID_CREDENTIALS` |
| 403 | Authenticated user lacks the role for the action | `FORBIDDEN` |
| 404 | Entity not found | `NOT_FOUND` |
| 409 | Conflict with existing data (duplicate item code, run already in progress) | `ITEM_CODE_EXISTS`, `RUN_IN_PROGRESS` |
| 422 | Request body or import file fails validation | `VALIDATION_ERROR`, `IMPORT_VALIDATION_FAILED` |
| 500 | Unexpected server error; the body never contains stack traces | `INTERNAL_ERROR` |

---

## 6. Acceptance criteria

Acceptance criteria are written as a short checklist (AC-xx.n) and, where the owner has completed them, as Given / When / Then scenarios that are the basis for tests in `backend/tests/`, `forecasting/tests/` and for the demo scripts of the verification plan. Criteria for the remaining requirements are **to be added** by the owners named below.

| Requirement | Owner of criteria | Status |
|---|---|---|
| FR-01, FR-02, FR-03, FR-04, FR-08, FR-09, FR-10, FR-14, FR-15 | Abzal Bakhytov | scenarios present |
| FR-05 | Birkhanym Kazhymukhamet | checklist present |
| FR-06, FR-07, FR-17 | Evelina Penkova | checklist present (draft) |
| FR-11, FR-12, FR-13 | Abzal Bakhytov / Birkhanym Kazhymukhamet | to be added |
| FR-16, FR-18 | Evelina Penkova | to be added |
| NFR-01 … NFR-10 | per category owner | to be added |

### 6.1 FR-01 — Import consumption, stock and receipt data from CSV/XLSX files

- AC-01.1 A pharmacist or administrator can upload a file of type `consumption`, `stock`, `receipts` or `planned_receipts` in CSV or XLSX format through the web interface and through `POST /api/v1/imports`. The accepted column sets are defined in section 5.5.1 and in `docs/data/data-specification.md`.
- AC-01.2 Every upload creates an `import_batch` record with file name, source type, timestamp, user and final status; imported rows reference the batch so that an import can be traced and reviewed later.
- AC-01.3 A file that fails validation (FR-02) stores no data rows; the batch is kept with status `failed` and the list of errors.
- AC-01.4 After a successful import the user sees the number of rows imported, the items affected and the period covered (basis for FR-18).

Scenarios:

**Scenario FR-01-S1 — successful CSV import**

- Given an authenticated pharmacist and a `consumption.csv` whose header is `item_code,item_name,unit,period_start,quantity`, whose item codes exist in the catalogue and whose rows pass validation,
- When the file is sent to `POST /api/v1/imports` with `source_type=consumption`,
- Then the response is `201 Created` with the `import_batch` (`id`, `file_name`, `source_type`, `imported_at`, `user_id`, `status = "completed"`, `summary_json`), `summary_json` contains `rows_total`, `rows_imported`, `items_affected`, `period_from`, `period_to`, and one `consumption_record` per row exists with `import_batch_id` equal to the batch id.

**Scenario FR-01-S2 — XLSX import**

- Given the same data saved as an `.xlsx` workbook whose first sheet has the header in the first row,
- When the file is uploaded with the same `source_type`,
- Then the result is identical to FR-01-S1 (same records, same summary).

**Scenario FR-01-S3 — stock, receipts and planned receipts files**

- Given valid `stock.csv`, `receipts.csv` and `planned_receipts.csv` files,
- When each is uploaded with its `source_type`,
- Then `stock_snapshot`, `receipt` and `planned_receipt` rows are created respectively, each linked to its batch, and `stock_snapshot.is_stock_out` is set to `true` for rows with `quantity_on_hand = 0` (FR-17).

**Scenario FR-01-S4 — unsupported file type**

- Given a `.pdf` file,
- When it is uploaded,
- Then the response is `400` with `code = "UNSUPPORTED_FILE_TYPE"`, an `import_batch` with `status = "failed"` and the error in `summary_json` is kept for the audit log, and no data rows are created.

**Scenario FR-01-S5 — viewer cannot import**

- Given an authenticated viewer,
- When a valid file is uploaded,
- Then the response is `403` with `code = "FORBIDDEN"` and no batch is created.

**Scenario FR-01-S6 — import is visible afterwards**

- Given a completed or failed batch,
- When `GET /api/v1/imports/{id}` is called by any authenticated user,
- Then the batch with its status and `summary_json` is returned, and the import appears in the import history page of the web interface.

### 6.2 FR-02 — Validate imported data and report errors

- AC-02.1 A file with a missing required column is rejected and the message names the missing column(s).
- AC-02.2 Rows with a negative quantity, an unknown item code or a duplicate (item, period) pair are reported with the row number, the column and the offending value.
- AC-02.3 The validation report is shown in the web interface after upload and is available through `GET /api/v1/imports/{id}`.
- AC-02.4 Validation is all-or-nothing per file: if any error is found, no rows of that file are stored.

Scenarios:

**Scenario FR-02-S1 — missing column**

- Given a `stock.csv` without the `quantity_on_hand` column,
- When it is uploaded,
- Then the response is `422` with `code = "IMPORT_VALIDATION_FAILED"` and a detail `{"column": "quantity_on_hand", "message": "required column is missing"}`, the batch is stored with `status = "failed"`, and no `stock_snapshot` rows are created.

**Scenario FR-02-S2 — negative quantity**

- Given a `consumption.csv` in which row 15 has `quantity = -3`,
- When it is uploaded,
- Then the response is `422` with a detail `{"row": 15, "column": "quantity", "value": "-3", "message": "quantity must be >= 0"}` and no rows of the file are stored.

**Scenario FR-02-S3 — unknown item code**

- Given a `receipts.csv` with an `item_code` that does not exist in the catalogue,
- When it is uploaded,
- Then the response is `422` with a detail naming the row, the column `item_code` and the unknown value, with `message = "unknown item code"`.

**Scenario FR-02-S4 — duplicate period**

- Given a `consumption.csv` with two rows for the same `item_code` and `period_start`,
- When it is uploaded,
- Then the response is `422` with a detail for the second occurrence (`column = "period_start"`, `message = "duplicate period for item"`).

**Scenario FR-02-S5 — period is not a Monday**

- Given a `consumption.csv` with a `period_start` that is not a Monday,
- When it is uploaded,
- Then the response is `422` with `message = "period_start must be a Monday"` for that row.

**Scenario FR-02-S6 — all-or-nothing**

- Given a file of 1,000 rows of which exactly one is invalid,
- When it is uploaded,
- Then no rows are stored, the summary reports `rows_total = 1000` and `errors_total = 1`, and the user can download or view the full error list from the import page.

**Scenario FR-02-S7 — error cap**

- Given a file with 250 invalid rows,
- When it is uploaded,
- Then `details` contains the first 100 errors and the `message` states the total of 250.

### 6.3 FR-03 — Maintain the medicine catalogue

- AC-03.1 A pharmacist or administrator can create and edit items with code, name, unit, group and active flag; the item code is unique.
- AC-03.2 Deactivating an item keeps its history and forecasts but excludes it from new forecast runs and from the risk list by default.
- AC-03.3 The item list can be searched by code and name and filtered by group and active flag.
- AC-03.4 A viewer can see the catalogue but cannot modify it.

Scenarios:

**Scenario FR-03-S1 — create item**

- Given an authenticated pharmacist,
- When `POST /api/v1/items` is called with `{"code": "A10BA02", "name": "Metformin 500 mg tab", "unit": "tab", "group": "A10"}`,
- Then the response is `201` with the created `medicine_item` and `is_active = true` by default.

**Scenario FR-03-S2 — duplicate code**

- Given an item with code `A10BA02` exists,
- When another item with the same code is created,
- Then the response is `409` with `code = "ITEM_CODE_EXISTS"`.

**Scenario FR-03-S3 — required fields**

- Given a request without `unit`,
- When it is sent to `POST /api/v1/items`,
- Then the response is `422` with a detail `{"field": "unit", "message": "field required"}`.

**Scenario FR-03-S4 — deactivate item**

- Given an active item with consumption history and forecasts,
- When the item is updated with `is_active = false`,
- Then its history and forecasts remain readable, it is excluded from new forecast runs unless explicitly selected, and it is hidden from the risk list by default.

**Scenario FR-03-S5 — search and filter**

- Given items in groups `A10` and `J01`,
- When `GET /api/v1/items?search=metf&group=A10&is_active=true` is called,
- Then only active items of group `A10` whose code or name contains `metf` (case-insensitive) are returned, with pagination fields.

**Scenario FR-03-S6 — viewer is read-only**

- Given an authenticated viewer,
- When `POST /api/v1/items` or an update is attempted,
- Then the response is `403`, while `GET /api/v1/items` succeeds.

### 6.4 FR-04 — Maintain suppliers and lead times per item

- AC-04.1 A pharmacist or administrator can create suppliers and link an item to one or more suppliers with `lead_time_days` and an `is_primary` flag.
- AC-04.2 Exactly one supplier per item is primary; its lead time is used by the risk calculation (FR-08).
- AC-04.3 An item without a supplier link uses the default lead time from the threshold configuration (FR-11).

Scenarios:

**Scenario FR-04-S1 — create supplier and link**

- Given an authenticated pharmacist and an item,
- When a supplier `SK-Pharmacy` is created and linked to the item with `lead_time_days = 21` and `is_primary = true`,
- Then an `item_supplier` row exists with these values and the item page shows the supplier and lead time.

**Scenario FR-04-S2 — single primary supplier**

- Given an item with a primary supplier,
- When a second supplier is linked with `is_primary = true`,
- Then the second becomes primary, the first is set to `is_primary = false`, and the change is written to the audit log (FR-15).

**Scenario FR-04-S3 — lead time validation**

- Given a link request with `lead_time_days = -5` or a non-integer value,
- When it is sent,
- Then the response is `422` with a detail for `lead_time_days`.

**Scenario FR-04-S4 — lead time used by risk**

- Given an item whose primary supplier has `lead_time_days = 21` and a completed forecast run,
- When the risk is calculated,
- Then the High threshold for that item is 21 days after the risk calculation date (see FR-08-S1).

**Scenario FR-04-S5 — default lead time**

- Given an item without any supplier link and `threshold_config.default_lead_time_days = 28`,
- When the risk is calculated,
- Then 28 days is used and the risk list marks the lead time as "default".

### 6.5 FR-05 — View current stock and consumption history per item

- AC-05.1 The item page shows the current stock (latest stock snapshot with its date) and the weekly consumption history as a table and as a line chart.
- AC-05.2 Weeks flagged as stock-out (FR-17) are visually marked in the chart and in the table.
- AC-05.3 The user can choose the history range (last 26 weeks, last 52 weeks, all) and the chart updates without reloading the page.
- AC-05.4 The page is usable at 1280 px width (NFR-09) and loads within 2 seconds for an item with 3 years of history (NFR-02).

### 6.6 FR-06 — Run a forecast for all or selected items

- AC-06.1 A pharmacist or administrator can start a forecast run for all active items or for a selected subset, choosing the horizon in weeks (default 12).
- AC-06.2 The run is recorded as a `forecast_run` with status (`queued`, `running`, `completed`, `failed`), model name and configuration, and its progress is visible in the interface.
- AC-06.3 A completed run contains one forecast row per item and per week of the horizon.
- AC-06.4 Items with insufficient history are listed in the run summary with a reason; they are not silently skipped.

### 6.7 FR-07 — View the forecast per item

- AC-07.1 The item forecast view shows history and forecast on one chart: the point forecast, the lower and upper bounds of the interval, and a visual boundary between history and forecast.
- AC-07.2 The view shows the model name, the run date, the horizon and a link to the run.
- AC-07.3 The same values are available as a table and through `GET /api/v1/items/{id}/forecast`.

### 6.8 FR-08 — Calculate shortage risk per item

- AC-08.1 For every item of a completed forecast run the system computes the projected stock per week as `current stock + planned receipts due by that week − cumulative forecast up to that week`.
- AC-08.2 The expected stock-out date is the first week in which the projected stock is less than or equal to the safety stock of the item.
- AC-08.3 The risk level is **High** if the stock-out is expected within the item's lead time, **Medium** if within the forecast horizon, **Low** otherwise.
- AC-08.4 The result is stored as a `risk_assessment` with the risk level, the expected stock-out date and the projected stock series.

Definitions used by the scenarios: `t0` is the Monday of the first forecast week (the week after the latest stock snapshot of the item); week `k` of the horizon starts at `t0 + 7·(k−1)` days; `current_stock` is the latest `stock_snapshot.quantity_on_hand`; planned receipts "due by week k" are `planned_receipt` rows with `status = "planned"` and `expected_on` earlier than the start of week `k+1`; the point forecast is used for the cumulative demand; `safety_stock` comes from the item's configuration or the global default (FR-11); the expected stock-out date is the start of the first week `k*` with `projected_stock(k*) ≤ safety_stock`; the risk calculation date is `t0`.

Scenarios:

**Scenario FR-08-S1 — High risk**

- Given an item with `current_stock = 100`, a 12-week point forecast of 30 units per week, no planned receipts, `safety_stock = 10` and `lead_time_days = 21`,
- When the risk is calculated,
- Then `projected_stock = [70, 40, 10, −20, …]`, the expected stock-out date is `t0 + 14 days` (week 3), which is within 21 days of `t0`, so `risk_level = "high"`.

**Scenario FR-08-S2 — planned receipt postpones the stock-out**

- Given the item of FR-08-S1 and a planned receipt of 60 units with `expected_on` in week 2 and `status = "planned"`,
- When the risk is calculated,
- Then `projected_stock = [70, 100, 70, 40, 10, …]`, the expected stock-out date is `t0 + 28 days` (week 5), which is later than the lead time but within the 12-week horizon, so `risk_level = "medium"`.

**Scenario FR-08-S3 — Low risk**

- Given an item with `current_stock = 1000` and a forecast of 30 units per week,
- When the risk is calculated for a 12-week horizon,
- Then the projected stock never falls to the safety stock within the horizon, `risk_level = "low"` and `expected_stockout_date` is `null`.

**Scenario FR-08-S4 — cancelled and received planned receipts are ignored**

- Given a planned receipt with `status = "cancelled"` or `status = "received"`,
- When the risk is calculated,
- Then that receipt is not added to the projected stock.

**Scenario FR-08-S5 — result is stored**

- Given a completed risk calculation,
- When `risk_assessment` rows are read for the run,
- Then every item of the run has exactly one row with `run_id`, `item_id`, `risk_level`, `expected_stockout_date`, `projected_stock_json` (list of `{period_start, projected_stock}`) and `computed_at`.

**Scenario FR-08-S6 — missing stock snapshot**

- Given an item with consumption history but no stock snapshot,
- When the risk is calculated,
- Then the item receives no risk level, is listed in the run summary under "no stock data" and is shown on the dashboard as "stock unknown" rather than as Low.

### 6.9 FR-09 — Show a prioritised list of items at risk

- AC-09.1 The risk list is ordered High → Medium → Low and, within a level, by expected stock-out date ascending.
- AC-09.2 The list can be filtered by risk level (`GET /api/v1/risks?level=high|medium|low`) and shows item code, name, group, current stock, lead time, expected stock-out date and risk level.
- AC-09.3 Every row links to the item page with its forecast.

Scenarios:

**Scenario FR-09-S1 — ordering**

- Given items A (high, stock-out `t0 + 14 d`), B (high, stock-out `t0 + 7 d`), C (medium, `t0 + 35 d`) and D (low),
- When `GET /api/v1/risks` is called without a filter,
- Then the order is B, A, C, D.

**Scenario FR-09-S2 — filter by level**

- Given the items of FR-09-S1,
- When `GET /api/v1/risks?level=high` is called,
- Then only B and A are returned; an unknown level value returns `400`.

**Scenario FR-09-S3 — latest run by default**

- Given two completed forecast runs,
- When the risk list is requested without `run_id`,
- Then the assessments of the most recent completed run are returned and the response states the run id and its `finished_at`.

**Scenario FR-09-S4 — row content**

- Given a risk assessment,
- When the list is rendered in the web interface,
- Then each row shows item code, name, group, current stock, lead time (with a "default" marker when no supplier is linked), expected stock-out date, risk level with a colour badge, and a link to the item page.

**Scenario FR-09-S5 — inactive items hidden**

- Given an inactive item with a risk assessment from an earlier run,
- When the list is requested,
- Then the item is not shown unless `include_inactive=true` is passed.

### 6.10 FR-10 — Record planned deliveries (expected receipts)

- AC-10.1 A pharmacist or administrator can record a planned receipt (item, expected date, quantity, supplier) in the interface, through the API and through `planned_receipts.csv`.
- AC-10.2 Planned receipts have a status (`planned`, `received`, `cancelled`); only `planned` ones are used in the risk calculation (FR-08).
- AC-10.3 Changing a planned receipt is reflected in the next risk calculation and recorded in the audit log.

Scenarios:

**Scenario FR-10-S1 — create planned receipt**

- Given an authenticated pharmacist, an item and a supplier,
- When a planned receipt with `expected_on = 2026-11-30` and `quantity = 60` is created,
- Then a `planned_receipt` row exists with `status = "planned"` and the item page lists it under "Expected deliveries".

**Scenario FR-10-S2 — validation**

- Given a request with `quantity = 0` or a negative quantity,
- When it is sent,
- Then the response is `422` with a detail for `quantity`.

**Scenario FR-10-S3 — status change**

- Given a planned receipt with `status = "planned"`,
- When its status is changed to `received` or `cancelled`,
- Then it is no longer counted in the projected stock of the next risk calculation and the change is written to the audit log with the old and new status.

**Scenario FR-10-S4 — import from file**

- Given a valid `planned_receipts.csv`,
- When it is imported,
- Then one `planned_receipt` row per file row is created with `status = "planned"` and linked to the import batch.

### 6.11 FR-14 — Authenticate users and manage roles

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

Scenarios:

**Scenario FR-14-S1 — successful login**

- Given an active user with role `pharmacist`,
- When `POST /api/v1/auth/login` is called with the correct e-mail and password,
- Then the response is `200` with an access token, its expiry time and the user's `id`, `full_name` and `role`; the token is accepted by the other endpoints as `Authorization: Bearer <token>`.

**Scenario FR-14-S2 — failed login**

- Given a wrong password, a non-existent e-mail or a deactivated user,
- When `POST /api/v1/auth/login` is called,
- Then the response is `401` with `code = "INVALID_CREDENTIALS"` and the same message in all three cases.

**Scenario FR-14-S3 — missing token**

- Given no `Authorization` header,
- When any endpoint except `/api/v1/health` and `/api/v1/auth/login` is called,
- Then the response is `401` with `code = "UNAUTHENTICATED"`.

**Scenario FR-14-S4 — role enforcement**

- Given an authenticated viewer,
- When `POST /api/v1/imports`, `POST /api/v1/forecast-runs` or `PUT /api/v1/config/thresholds` is called,
- Then the response is `403` with `code = "FORBIDDEN"`, and the corresponding buttons are not shown in the web interface.

**Scenario FR-14-S5 — user management**

- Given an authenticated administrator,
- When a user is created with e-mail, full name, role and initial password,
- Then an `app_user` row exists with a `password_hash` produced by a salted password-hashing function, the plain password is not stored or logged, `GET` responses never contain `password_hash`, and the action is written to the audit log.

**Scenario FR-14-S6 — deactivation**

- Given an active user,
- When the administrator sets `is_active = false`,
- Then the user's existing tokens are rejected with `401` and new logins fail as in FR-14-S2.

### 6.12 FR-15 — Keep an audit log

- AC-15.1 Imports (completed and failed), forecast runs (started, completed, failed) and configuration changes are written to `audit_log` with user, action, entity, entity id, timestamp and details.
- AC-15.2 Changes to users, suppliers and planned receipts are also logged (team decision; extends the minimum scope of FR-15).
- AC-15.3 The audit log is append-only from the application's point of view and is readable by administrators with filters by user, action and date range.

Scenarios:

**Scenario FR-15-S1 — import is logged**

- Given a completed or failed import,
- When the audit log is read,
- Then an entry exists with `action = "import.completed"` or `"import.failed"`, `entity = "import_batch"`, `entity_id` = batch id, `user_id` = uploader, and `details_json` containing the file name and the summary.

**Scenario FR-15-S2 — forecast run is logged**

- Given a forecast run,
- When it starts and when it finishes,
- Then entries `forecast_run.started` and `forecast_run.completed` (or `forecast_run.failed`) exist with `entity = "forecast_run"` and `details_json` containing `horizon_weeks`, `model_name` and the item count.

**Scenario FR-15-S3 — configuration change is logged**

- Given `threshold_config` key `safety_stock_weeks` with value `2`,
- When an administrator changes it to `3` through `PUT /api/v1/config/thresholds`,
- Then an entry `config.updated` exists with `details_json = {"key": "safety_stock_weeks", "old": 2, "new": 3}`.

**Scenario FR-15-S4 — read access**

- Given an authenticated administrator,
- When `GET /api/v1/audit-log?user_id=…&action=…&from=…&to=…` is called (endpoint to be added to the draft API contract in `docs/architecture/api-contract.md`),
- Then matching entries are returned newest first with pagination; a pharmacist or viewer receives `403`.

**Scenario FR-15-S5 — no deletion through the API**

- Given any role,
- When a delete or update of an audit entry is attempted through the API,
- Then no such endpoint exists (`404`/`405`), and the database role used by the application has no `DELETE` privilege on `audit_log` (verified by inspection of the deployment configuration).

### 6.13 FR-17 — Flag stock-out periods (censored demand)

- AC-17.1 A week whose stock snapshot shows zero quantity on hand is flagged `is_stock_out` for that item.
- AC-17.2 Zero consumption in a flagged week is passed to the forecasting module as censored, not as an observed zero; the handling method is documented in the forecasting module.
- AC-17.3 Flagged weeks are visible on the item page (FR-05) and counted in the data-quality summary (FR-18).

### 6.14 Acceptance criteria to be added

FR-11, FR-12, FR-13, FR-16, FR-18 and NFR-01 … NFR-10: to be added.

---

## 7. Open questions

| # | Question | Affects | How it will be resolved |
|---|---|---|---|
| Q1 | Are lead times maintained per supplier, per item or per item-supplier pair in practice? | FR-04, FR-08 | Stakeholder interview |
| Q2 | Should unknown item codes in `consumption.csv` (which carries name and unit) create catalogue entries automatically, or always be rejected? | FR-02, FR-03 | Stakeholder interview; default is to reject |
| Q3 | Which report formats and columns are needed for management (CSV, XLSX, both)? | FR-13 | Stakeholder interview |
| Q4 | Is a 12-week horizon with a weekly step adequate for centralised procurement cycles? | FR-06, FR-08 | Stakeholder interview; data analysis |
| Q5 | Will real historical data be available before December 2026? | all experiments | Partner organization; tracked in `docs/project-management/risks.md` |
| Q6 | Should the risk calculation use the point forecast or the upper bound of the interval for conservative planning? | FR-08, FR-11 | Decision after the first hold-out evaluation; point forecast until then, configurable later |

---

## 8. Revision history

| Date | Version | Author | Change |
|---|---|---|---|
| 2026-10-16 | 0.1 | Birkhanym Kazhymukhamet | Initial version: introduction, stakeholders and roles, FR-01…FR-18, NFR-01…NFR-10, constraints, acceptance criteria for Must requirements |
| 2026-10-17 | 0.2 | Abzal Bakhytov | Added section 5.5 "Data and API constraints"; Given/When/Then scenarios for FR-01, FR-02, FR-03, FR-08, FR-09, FR-14; new criteria and scenarios for FR-04, FR-10, FR-15; open question Q6 |
