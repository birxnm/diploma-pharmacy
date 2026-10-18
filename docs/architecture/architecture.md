# PharmaStock — Architecture description

Task: PHA2-12 · Primary author: Abzal Bakhytov · Status: draft for review · Last updated: 2026-10-18

This document describes the architecture of PharmaStock, the prototype developed in the
diploma project "Development of smart supply chain analytics system for forecasting
pharmaceutical inventory and preventing medicine shortages in healthcare organizations"
(Astana IT University, group SE-2414, 2026–2027). It is the entry point for the other
architecture documents:

| Document | Content | State |
|---|---|---|
| `docs/architecture/architecture.md` (this file) | Goals, context, high-level overview, components, flows, deployment, decisions, requirement alignment | Draft for review |
| `docs/architecture/api-contract.md` | REST API v1 endpoints, request/response schemas | In progress |
| `docs/architecture/database-schema.md` | Tables, keys, constraints, migrations | In progress |
| `docs/requirements.md` | Functional (FR) and non-functional (NFR) requirements | In progress |
| `docs/technology-comparison.md` | Justification of the technology stack | In progress |
| `docs/diagrams/src/*.mmd`, `docs/diagrams/export/*.svg` | Diagram sources (Mermaid) and exports | See below |

Task tracking: [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b).

Contents: 1 Architectural goals · 2 System context · 3 High-level overview ·
4 Component view · 5 Key flows · 6 Technology mapping · 7 Deployment view ·
8 Cross-cutting concerns · 9 Architectural decisions · 10 Alignment with requirements ·
11 Next steps.

## 1. Architectural goals

The goals below drive the decisions in this document. They are derived from the
requirements (`docs/requirements.md`) and from the project constraints (three-person team,
one academic year, uncertain access to real data).

| ID | Goal | Driven by |
|---|---|---|
| AG-1 | Correct treatment of intermittent and censored demand: stock-out periods are flagged and zero consumption during a stock-out is never learned as zero demand | FR-17, NFR-06 |
| AG-2 | Reproducible forecasting: fixed seeds, versioned configurations, saved results for every forecast run and experiment | FR-16, NFR-05 |
| AG-3 | Security and privacy by design: role-based access, hashed passwords, audit trail, no patient data anywhere in the system | FR-14, FR-15, NFR-03, NFR-04 |
| AG-4 | Few moving parts: a single backend service, one database, the forecasting module as an in-process library, so that three students can build, test and deploy the system | NFR-07, NFR-08 |
| AG-5 | Predictable performance for a hospital-scale catalogue (up to 5,000 items, forecast run for 1,000 items with 3 years of weekly history within 5 minutes) | NFR-01, NFR-02 |
| AG-6 | Clear ownership boundaries that match the team responsibilities: frontend, backend and forecasting communicate only through two documented contracts (REST API and the forecasting package interface) | Team structure, `docs/project-management/responsibilities.md` |
| AG-7 | Replaceable data sources: the prototype works with a documented synthetic dataset and switches to real exports without code changes beyond the importer | Data access risk, `docs/project-management/risks.md` |

## 2. System context

PharmaStock is an internal web application of one healthcare organization. It does not
process patient data and it does not execute procurement; it turns historical consumption,
current stock, planned receipts and lead times into per-item consumption forecasts and
shortage-risk signals that pharmacy and procurement staff act on.

Context diagram: `docs/diagrams/export/system-context.svg` (source:
`docs/diagrams/src/system-context.mmd`; the SVG export is produced from the Mermaid source).

![System context diagram](../diagrams/export/system-context.svg)

### 2.1 Users

| Actor | Role in the organization | Role in PharmaStock (FR-14) | Main interactions |
|---|---|---|---|
| Head of hospital pharmacy / pharmacist | Owns the pharmacy stock | `pharmacist` | Uploads export files, maintains the catalogue, runs forecasts, reviews the risk list and item pages, configures thresholds |
| Procurement and supply specialist | Plans purchases and deliveries | `pharmacist` | Records planned deliveries and lead times, uses the prioritised risk list and reports |
| Head of clinical department | Consumes medicines in the department | `viewer` | Views forecasts and risk status for the department's medicines (read only) |
| System administrator | Operates the installation | `administrator` | Manages users and roles, reviews the audit log, maintains the deployment |

The three application roles (`administrator`, `pharmacist`, `viewer`) are defined in FR-14;
the mapping above is the initial assumption and is revisited in the requirements work.

### 2.2 External systems and data sources

| External element | Direction | How it enters the system | Notes |
|---|---|---|---|
| Hospital accounting system / medical information system (MIS) | Into PharmaStock | CSV/XLSX export files (`consumption.csv`, `stock.csv`, `receipts.csv`) uploaded manually by the pharmacist | No real-time integration with 1C or national systems in the prototype (scope OUT, future work) |
| SK-Pharmacy delivery schedules | Into PharmaStock | Planned deliveries entered manually or imported as `planned_receipts.csv` | Centralised procurement for the guaranteed volume of free medical care; the schedule is a document, not an API |
| Users' browsers | Both | HTTPS | Current Chrome, Firefox and Edge on desktop, responsive down to 1280 px (NFR-09) |

Deliberately not in the context: e-mail or messenger gateways (notifications are in-app
only, FR-12), ordering or procurement systems (scope OUT), mobile applications (scope OUT),
other organizations (single-organization deployment, no multi-tenant SaaS).

## 3. High-level overview

PharmaStock is a three-tier web application with one additional in-process component,
the forecasting package.

```mermaid
flowchart LR
    users["Pharmacy users<br/>(browser)"]
    files["CSV/XLSX export files<br/>MIS exports, delivery schedules"]
    subgraph app ["PharmaStock"]
        spa["Web interface<br/>Vue 3 single-page application"]
        api["Backend<br/>FastAPI service"]
        jobs["Background job runner<br/>and scheduler"]
        fc["Forecasting package<br/>in-process Python library"]
        db[("PostgreSQL 16")]
    end
    users -->|"HTTPS"| spa
    files -. "manual upload" .-> spa
    spa -->|"REST API /api/v1, JSON"| api
    api --> db
    api --> jobs
    jobs -->|"forecast_items(history, horizon, config)"| fc
    jobs --> db
```

| Element | Responsibility | Owner |
|---|---|---|
| Web interface (`frontend/`) | Single-page application for all user interactions: dashboards, item pages with history and forecast charts, prioritised risk list, imports, settings. Talks to the backend only through the REST API. | Birkhanym Kazhymukhamet |
| Backend (`backend/`) | FastAPI service exposing REST API v1; authentication and roles; medicine catalogue; importer; forecast runs; shortage-risk calculation; notifications; audit log; configuration; report export. | Abzal Bakhytov |
| Importer (part of the backend) | Parses uploaded CSV/XLSX files, validates them (FR-02), flags stock-out periods (FR-17), produces a data-quality summary (FR-18) and stores records linked to an `import_batch`. | Abzal Bakhytov |
| Background job runner and scheduler (part of the backend) | Executes long-running work outside the request cycle: forecast runs triggered by `POST /api/v1/forecast-runs` and periodic runs (planned: weekly after the import). Updates `forecast_run.status` so that the interface can poll progress. | Abzal Bakhytov |
| Forecasting package (`forecasting/`) | Pure Python library called in-process by the job runner: data validation, feature preparation, baselines (naive, seasonal naive, moving average, Croston, SBA), ML models, evaluation (MAE, WAPE, bias, rolling-origin split). Entry point `forecasting.api.forecast_items(history, horizon, config) -> ForecastResult`. Has no database access and no knowledge of HTTP. | Evelina Penkova |
| Database (PostgreSQL 16) | Single relational store for the catalogue, imported time series, forecasts, risk assessments, notifications, users, audit log and configuration (entities listed in `docs/architecture/database-schema.md`). | Abzal Bakhytov |

Request path: the browser loads the SPA as static files and calls the backend at
`/api/v1/...` with a bearer token obtained from `POST /api/v1/auth/login`. The backend
reads and writes PostgreSQL through SQLAlchemy 2.x; schema changes are applied with Alembic
migrations.

Forecast path: a forecast run is created as a `forecast_run` row with status `queued` and
handed to the job runner. The runner loads the weekly history (consumption with stock-out
flags), calls `forecasting.api.forecast_items`, stores one `forecast` row per item and
week, computes a `risk_assessment` per item (projected stock = current stock + planned
receipts due by week t − cumulative forecast up to t; expected stock-out date = first week
where projected stock ≤ safety stock; High if within lead time, Medium if within the
horizon, Low otherwise) and creates in-app `notification` rows for high-risk items.

Weekly granularity: all time-series tables store `period_start`, the Monday of the ISO
week, as the period key; the initial horizon is 12 weeks and is configurable per run
(`forecast_run.horizon_weeks`).

## 4. Component view

Component diagram (draft): `docs/diagrams/export/component-diagram.svg` (source:
`docs/diagrams/src/component-diagram.mmd`).

![Component diagram](../diagrams/export/component-diagram.svg)

The diagram groups the components into five areas: the frontend, the backend, the
forecasting package, the database and the external file sources. Arrows show synchronous
calls; dotted arrows show manual upload or entry by a user.

### 4.1 Component responsibilities

| Area | Component | Responsibility | Data entities touched | Owner |
|---|---|---|---|---|
| Frontend | Dashboard view | Summary of the latest forecast run: counts of items by risk level, recent imports, unread notifications | — (via API) | Birkhanym |
| Frontend | Items view | Catalogue list and item page: current stock, consumption history as table and chart, suppliers and lead times | — (via API) | Birkhanym |
| Frontend | Forecast view | Start a forecast run for all or selected items with a horizon, follow run status, show point forecast, interval and model information per item together with history | — (via API) | Birkhanym |
| Frontend | Risks view | Prioritised risk list with risk level, expected stock-out date and projected stock; filters by level; CSV export link | — (via API) | Birkhanym |
| Frontend | Imports view | Upload CSV/XLSX files, show validation errors and the data-quality summary per import | — (via API) | Birkhanym |
| Frontend | Settings view | Risk thresholds and safety-stock parameters; user and role management for administrators | — (via API) | Birkhanym |
| Frontend | API client | Typed HTTP client generated from the OpenAPI schema plus Pinia stores for session, catalogue, runs and notifications; attaches the bearer token; maps API errors to user messages | — | Birkhanym |
| Backend | Application entry point (`backend/app/main.py`) | Creates the FastAPI application, mounts the routers under `/api/v1`, registers error handlers and CORS; `GET /api/v1/health` for Docker Compose health checks and the CI smoke test | — | Abzal |
| Backend | `auth` router | `POST /api/v1/auth/login`; issues bearer tokens; dependency that resolves the current user and checks roles | `app_user` | Abzal |
| Backend | `items` router | `GET/POST /api/v1/items`, `GET /api/v1/items/{id}/history`, `GET /api/v1/items/{id}/forecast` | `medicine_item`, `consumption_record`, `stock_snapshot`, `forecast` | Abzal |
| Backend | `imports` router | `POST /api/v1/imports` (file upload), `GET /api/v1/imports/{id}` (status, errors, data-quality summary) | `import_batch` | Abzal |
| Backend | `forecast-runs` router | `POST /api/v1/forecast-runs`, `GET /api/v1/forecast-runs/{id}` | `forecast_run` | Abzal |
| Backend | `risks` router | `GET /api/v1/risks?level=high\|medium\|low`, `GET /api/v1/reports/risks.csv` (report export; a separate `reports` router is split out if more report types are added) | `risk_assessment` | Abzal |
| Backend | `notifications` router | `GET /api/v1/notifications`, mark as read | `notification` | Abzal |
| Backend | `config` router | `GET/PUT /api/v1/config/thresholds` | `threshold_config` | Abzal |
| Backend | ImportService | Parses CSV/XLSX, calls the validation rules, flags stock-out periods, updates name and unit of catalogue items found in files (unknown codes are rejected, FR-02), stores records and the summary, sets `import_batch.status` | `import_batch`, `medicine_item`, `consumption_record`, `stock_snapshot`, `receipt`, `planned_receipt` | Abzal |
| Backend | CatalogueService | Medicine catalogue, suppliers and lead times, history queries for item pages | `medicine_item`, `supplier`, `item_supplier` | Abzal |
| Backend | ForecastService | Creates and tracks forecast runs, prepares the history table for the forecasting package, stores forecasts, records the configuration used | `forecast_run`, `forecast` | Abzal, with Evelina for the data contract |
| Backend | RiskService | Shortage-risk calculation per item (projected stock, expected stock-out date, risk level) using thresholds and lead times; owns threshold configuration | `risk_assessment`, `planned_receipt`, `item_supplier`, `threshold_config` | Abzal |
| Backend | NotificationService | Creates in-app notifications for high-risk items after each run; read/unread state per user | `notification` | Abzal |
| Backend | AuditService | Writes audit entries for imports, forecast runs, configuration changes and user management | `audit_log` | Abzal |
| Backend | Repositories | SQLAlchemy 2.x models and query functions per entity; sessions per request and per job; Alembic migrations | all | Abzal |
| Backend | Background job runner and scheduler | Executes queued forecast runs one at a time and periodic runs; isolates failures and records them in `forecast_run.status` | `forecast_run` | Abzal |
| Forecasting | Data validation (`forecasting/forecasting/data/schema.py`, `validation.py`) | Schema of the history table, checks for missing columns, negative quantities, duplicate periods, irregular weeks; rejects malformed input with a clear error (NFR-06) | — | Evelina |
| Forecasting | Feature preparation | Resampling to a regular weekly series, censored-demand handling for stock-out weeks, lags, rolling statistics, calendar features, item group attributes | — | Evelina |
| Forecasting | Baselines (`models/baselines.py`) | naive, seasonal_naive (season 52), moving_average(window), croston, sba | — | Evelina |
| Forecasting | ML models | Gradient boosting (LightGBM) on lag and calendar features; statistical models from statsforecast; global models across items — candidates, final choice after experiments | — | Evelina |
| Forecasting | Evaluation (`evaluation/metrics.py`, `evaluation/split.py`) | mae, wape (None when the sum of actuals is 0), bias; time-based rolling-origin split with train/validation/test by date | — | Evelina |
| Forecasting | `forecasting.api` | `forecast_items(history, horizon, config) -> ForecastResult`: the single entry point used by the backend | — | Evelina, with Abzal for integration |
| Database | PostgreSQL 16 | Persistent storage; one schema managed by Alembic | all | Abzal |

### 4.2 Contracts between the areas

| Contract | Between | Where it is defined |
|---|---|---|
| REST API v1 | Frontend ↔ Backend | `docs/architecture/api-contract.md`; OpenAPI schema that FastAPI produces |
| Forecasting package interface | Backend ↔ Forecasting | `forecasting/README.md`, `forecasting/forecasting/api.py`, history schema in `forecasting/forecasting/data/schema.py` |
| Import file formats | Users/MIS ↔ Backend | `docs/data/data-specification.md`: `consumption.csv`, `stock.csv`, `receipts.csv`, `planned_receipts.csv` (CSV, UTF-8, header row, `period_start` = Monday of the week, ISO date) |
| Database schema | Backend ↔ PostgreSQL | `docs/architecture/database-schema.md`; Alembic migrations in `backend/` |

## 5. Key flows

### 5.1 Import → validation → storage

```mermaid
sequenceDiagram
    actor P as Pharmacist
    participant UI as Imports view
    participant API as imports router
    participant IS as ImportService
    participant V as Validation rules
    participant R as Repositories
    participant DB as PostgreSQL
    participant AU as AuditService

    P->>UI: Select consumption.csv and upload
    UI->>API: POST /api/v1/imports (file, source_type)
    API->>IS: import_file(file, source_type, user)
    IS->>R: create import_batch (status processing)
    R->>DB: INSERT import_batch
    IS->>V: parse and validate rows
    V-->>IS: errors, warnings, data-quality summary
    alt blocking errors
        IS->>R: update import_batch (status failed, summary_json)
    else valid
        IS->>R: resolve items by item_code, insert consumption_record, stock_snapshot, receipt or planned_receipt rows
        R->>DB: INSERT rows with import_batch_id
        IS->>R: update import_batch (status completed, summary_json)
    end
    IS->>AU: record import (user, import_batch id, status)
    API-->>UI: 201 import_batch id, status, summary
    UI->>API: GET /api/v1/imports/{id}
    API-->>UI: status, errors, data-quality summary
```

Rules applied during validation (FR-02, FR-17, FR-18):

- blocking errors: missing columns, negative quantities, unknown item codes (codes absent
  from the medicine catalogue are listed so that the catalogue can be completed under
  FR-03 before the file is imported again), unparseable dates, duplicate
  `(item_code, period_start)` within one file, `period_start` that is not a Monday;
- warnings: gaps in the weekly series, outliers flagged by the data-quality rules;
- stock-out flag: a week is marked `stock_snapshot.is_stock_out = true` when
  `quantity_on_hand` is 0 at `period_start`; the forecasting package receives this flag
  with the history so that zero consumption in such weeks is treated as censored demand;
- the data-quality summary (coverage, gaps, outliers) is stored in
  `import_batch.summary_json` and shown in the Imports view.

### 5.2 Forecast run → forecasting package → forecasts, risk assessment, notifications

```mermaid
sequenceDiagram
    actor P as Pharmacist
    participant UI as Forecast view
    participant API as forecast-runs router
    participant FS as ForecastService
    participant J as Background job runner
    participant FP as forecasting package
    participant RS as RiskService
    participant NS as NotificationService
    participant DB as PostgreSQL (via repositories)

    P->>UI: Run forecast (items, horizon)
    UI->>API: POST /api/v1/forecast-runs
    API->>FS: create_run(items, horizon_weeks, config, user)
    FS->>DB: INSERT forecast_run (status queued, config_json)
    FS->>J: enqueue(run_id)
    API-->>UI: 202 run id, status queued
    J->>DB: UPDATE forecast_run (status running, started_at)
    J->>DB: load consumption_record and stock_snapshot history
    J->>FP: forecast_items(history, horizon, config)
    FP-->>J: ForecastResult (point, lower, upper, model info per item)
    J->>DB: INSERT forecast rows (run_id, item_id, period_start)
    J->>RS: assess(run_id)
    RS->>DB: load current stock, planned_receipt, lead times, threshold_config
    RS->>DB: INSERT risk_assessment per item
    RS->>NS: notify_high_risk(run_id)
    NS->>DB: INSERT notification per user and high-risk item
    J->>DB: UPDATE forecast_run (status completed, finished_at)
    loop until status is completed or failed
        UI->>API: GET /api/v1/forecast-runs/{id}
        API-->>UI: status, progress
    end
    UI->>API: GET /api/v1/items/{id}/forecast, GET /api/v1/risks?level=high
    API-->>UI: forecasts, prioritised risk list
```

Failure handling: if the forecasting package raises a validation error (NFR-06) or the run
fails for any other reason, the runner stores `forecast_run.status = failed`, no partial
`forecast` or `risk_assessment` rows are kept, and an audit entry with the error message in
`audit_log.details_json` is written. The interface shows the message in the Forecast view.

Risk calculation (FR-08, FR-09) per item for each week t of the horizon:

```text
projected_stock(t) = current_stock + planned receipts due by t − cumulative forecast up to t
expected stock-out date = first week where projected_stock(t) ≤ safety stock
risk level = High   if the stock-out is expected within the item's lead time
           = Medium if within the forecast horizon
           = Low    otherwise
```

`current_stock` is the latest `stock_snapshot` for the item, planned receipts come from
`planned_receipt` with status planned, lead time from the primary `item_supplier`, safety
stock and the level boundaries from `threshold_config`. The projected series is stored in
`risk_assessment.projected_stock_json` so that the Risks view can chart it.

## 6. Technology mapping

| Component | Technology | Notes |
|---|---|---|
| Web interface | Vue 3, Vite, TypeScript, Vue Router, Pinia, Chart.js | Built to static files; Vitest for unit tests (later) |
| Backend API | Python 3.12, FastAPI, Pydantic v2, uvicorn | OpenAPI schema generated; request validation at the boundary |
| Persistence | SQLAlchemy 2.x, Alembic, PostgreSQL 16 | JSONB columns for `summary_json`, `config_json`, `projected_stock_json`, `details_json`, `value_json` |
| Background jobs | In-process worker in the backend | See ADR-5; mechanism to be confirmed against NFR-01 during backend implementation |
| Forecasting | pandas, numpy, scikit-learn, statsforecast, LightGBM | Installed into the backend environment as the `forecasting` package (ADR-1) |
| Tests | pytest (backend, forecasting), Vitest (frontend, later) | Run in CI on every pull request (NFR-08) |
| Infrastructure | Docker Compose (PostgreSQL), GitHub Actions CI | `docker-compose.yml`, `.github/workflows/ci.yml` |
| Documentation | Markdown, Mermaid | Sources in `docs/diagrams/src/*.mmd`, exports in `docs/diagrams/export/*.svg` |

Justification of the choices: `docs/technology-comparison.md`.

## 7. Deployment view

Target: a single Linux host with Docker Compose (NFR-07). Three services:

```mermaid
flowchart LR
    browser["Browser<br/>Chrome, Firefox, Edge"]
    subgraph host ["Linux host: Docker Compose"]
        frontend["frontend<br/>static build of the SPA<br/>served by a static web server container"]
        backend["backend<br/>FastAPI + uvicorn<br/>forecasting package installed in the same image"]
        db[("db<br/>PostgreSQL 16<br/>named volume for data")]
    end
    browser -->|"HTTPS"| frontend
    browser -->|"HTTPS /api/v1"| backend
    backend -->|"TCP 5432"| db
```

| Service | Image / build | Configuration | Notes |
|---|---|---|---|
| `db` | `postgres:16` | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` from `.env`; data in a named volume | The only service needed for local backend development |
| `backend` | Built from `backend/` (Python 3.12 base image, installs `backend/` and `forecasting/`) | `DATABASE_URL`, `SECRET_KEY`, `LOG_LEVEL`, forecasting defaults from `.env`; Alembic migrations run on start | Runs uvicorn; the job runner lives in the same process |
| `frontend` | Built from `frontend/` (Vite build copied into a static web server image) | API base URL at build time | Serves the SPA; `/api/v1` requests go to `backend` |

- HTTPS is terminated by a reverse proxy in front of Compose in the deployed environment
  (NFR-03); in local development plain HTTP on localhost is used.
- `.env.example` documents every variable; secrets are never committed.
- Developer setup: `docker compose up db`, then run the backend with uvicorn and the
  frontend with the Vite dev server (documented in `backend/README.md` and
  `frontend/README.md`).
- CI (GitHub Actions) runs pytest for `backend/` and `forecasting/` with a PostgreSQL
  service container, and the frontend build on every pull request (NFR-08).

## 8. Cross-cutting concerns

### 8.1 Authentication and authorization (FR-14, NFR-03)

- `POST /api/v1/auth/login` with e-mail and password returns a signed bearer token with
  the user id and role; the token is sent in the `Authorization` header.
- Passwords are stored only as salted hashes in `app_user.password_hash`.
- Roles: `administrator` (users, roles, all data), `pharmacist` (imports, catalogue,
  forecast runs, thresholds, planned receipts, reports), `viewer` (read-only access to
  items, forecasts, risks and notifications). Permission checks are FastAPI dependencies
  on each router; the frontend hides actions the role cannot perform but does not enforce
  security.
- No patient data exists in any entity (NFR-04); the only personal data are the e-mail
  and full name of application users.

### 8.2 Audit log (FR-15)

AuditService writes an `audit_log` row (`user_id`, `action`, `entity`, `entity_id`,
`created_at`, `details_json`) for: imports (created, completed, failed), forecast runs
(created, completed, failed), threshold changes, planned-receipt changes, user and role
changes. Entries are written in the same database transaction as the change. The audit log
is readable by administrators in the Settings view (planned).

### 8.3 Configuration (FR-11, NFR-05)

| Kind | Where | Changed by |
|---|---|---|
| Infrastructure settings (database URL, secret key, log level, job concurrency) | Environment variables read by `backend/app/core/config.py` (Pydantic settings); documented in `.env.example` | Deployment |
| Domain thresholds (safety-stock rule, risk level boundaries, default horizon) | `threshold_config` table, `GET/PUT /api/v1/config/thresholds` | Pharmacist or administrator, audited |
| Forecast model configuration (model name, parameters, seed, feature set) | `forecast_run.config_json` for runs; versioned experiment configurations in `forecasting/experiments/` | Forecast run request; experiments by Evelina |

Every forecast run stores the full configuration it used, so results can be reproduced
from the database alone.

### 8.4 Logging and error handling

- Structured application logs through the Python `logging` module with a request id per
  HTTP request and a run id per background job; uvicorn access logs; log level from
  configuration. Logs contain no file contents and no user credentials.
- API errors follow one JSON shape (`detail`, `code`, optional `errors` list). Input
  validation errors return 422 with the offending fields; domain errors (unknown item,
  run not found, role not allowed) return 404, 403 or 409.
- The forecasting package validates its input before modelling and raises a typed
  exception with a clear message instead of producing a wrong forecast (NFR-06); the
  backend turns it into a failed import or failed run with the message visible to the user.

### 8.5 Data validation at the boundaries

Validation happens twice, with different purposes: Pydantic schemas validate API payloads
(types, required fields, enumerations); the importer and the forecasting package validate
the content of time series (negative quantities, duplicate periods, non-Monday
`period_start`, gaps, stock-out consistency). The rules are shared where possible so that
an import that passed validation can always be forecast.

## 9. Architectural decisions

Decisions are recorded in a short ADR style. Status is `Accepted` (the team builds on it)
or `Proposed` (to be confirmed by a measurement or a later task). A decision is changed
only by a new entry that supersedes it.

### ADR-1 Forecasting as an in-process Python package, not a separate service

- Status: Accepted (2026-10-18).
- Context: the forecasting module is developed by Evelina as the `forecasting/` package
  and the backend by Abzal. The backend must execute forecasts for up to 1,000 items
  within 5 minutes (NFR-01) and every run must be reproducible (NFR-05). Options
  considered: (a) a separate forecasting service with an HTTP API, (b) a task queue with
  dedicated worker processes, (c) a plain Python package imported by the backend.
- Decision: option (c). The backend installs `forecasting` into its own environment and
  the background job runner calls `forecasting.api.forecast_items(history, horizon,
  config) -> ForecastResult` directly. The package has no database or HTTP code; the
  backend converts between database rows and the history table.
- Consequences: one deployable service and one Python environment, no network
  serialisation of time series, the same code runs in experiments and in the application,
  and unit tests of the forecasting package need no backend. The backend image carries
  the ML dependencies (pandas, numpy, scikit-learn, statsforecast, LightGBM) and
  CPU-heavy runs share the process with the API, which ADR-5 addresses by running them in
  the background with limited concurrency. Because the integration point is a single
  function with plain data structures, a separate service remains possible later without
  changing the forecasting code.

### ADR-2 PostgreSQL as the single data store

- Status: Accepted (2026-10-18).
- Context: the system stores a catalogue, weekly time series per item, forecasts with
  intervals, risk assessments with a projected series, users, notifications, an audit log
  and configuration (entities in `docs/architecture/database-schema.md`). Options
  considered: SQLite, PostgreSQL, MySQL/MariaDB, a dedicated time-series database next to
  a relational one.
- Decision: PostgreSQL 16 as the only database, accessed through SQLAlchemy 2.x with
  Alembic migrations. Semi-structured payloads (`summary_json`, `config_json`,
  `projected_stock_json`, `details_json`, `value_json`) use JSONB columns.
- Consequences: mature transactional storage with constraints that protect data quality
  (unique `(item_id, period_start)` per batch, foreign keys), window functions for history
  and projection queries, JSONB for flexible run configurations and summaries, and a
  standard Docker image for local development and CI. Weekly data volumes (5,000 items ×
  156 weeks ≈ 780,000 rows per series) do not need a time-series database. Tests that
  touch the database run against a PostgreSQL service in CI rather than SQLite, so that
  JSONB and constraint behaviour is identical.

### ADR-3 REST/JSON API between the web interface and the backend

- Status: Accepted (2026-10-18).
- Context: the frontend (Birkhanym) and the backend (Abzal) are developed in parallel and
  need a contract that can be agreed early and tested independently. Options considered:
  REST with JSON, GraphQL, server-rendered pages.
- Decision: a resource-oriented REST API under `/api/v1` with JSON payloads, documented
  in `docs/architecture/api-contract.md` and served with the OpenAPI schema that FastAPI
  produces; CSV for report downloads (`GET /api/v1/reports/risks.csv`); bearer-token
  authentication. Long-running work is modelled as a resource (`forecast_run`) whose status
  is polled.
- Consequences: a small, well-understood surface that both pytest and the browser can
  exercise; the frontend can be developed against the contract and mocked responses; the
  OpenAPI schema can generate the typed client. There is no server push, so the Forecast
  view polls `GET /api/v1/forecast-runs/{id}` while a run is in progress (acceptable for
  runs lasting minutes). Purpose-built endpoints (`/items/{id}/history`,
  `/items/{id}/forecast`, `/risks`) avoid over-fetching without a query language.

### ADR-4 Weekly granularity stored as `period_start`

- Status: Accepted (2026-10-18); the time step itself remains open for revision until the
  requirements are frozen, as stated in the proposal.
- Context: medicine consumption is intermittent and daily records are sparse and noisy;
  procurement decisions are made on a weekly or longer cycle; the initial decision is a
  weekly step with a 12-week horizon. The storage representation must make aggregation,
  joins between consumption, stock, forecasts and risk projections, and validation
  unambiguous.
- Decision: every weekly table (`consumption_record`, `stock_snapshot`, `forecast`)
  stores `period_start`, the Monday of the ISO week, as a `DATE` column that is part of a
  uniqueness constraint with `item_id` (and the import batch where applicable). Receipts
  and planned receipts keep their exact dates (`received_on`, `expected_on`) and are
  aggregated to weeks when a projection is computed. Horizons are expressed in weeks
  (`forecast_run.horizon_weeks`). Import files must provide `period_start` as the Monday of
  the week in ISO format; other dates are rejected by validation.
- Consequences: one convention shared by the import formats, the database, the API and
  the forecasting package; weeks line up exactly across tables, which makes the risk
  projection a simple cumulative calculation; the stock-out flag is defined per week. If
  the time step is changed later, `period_start` keeps its meaning (start of the period)
  and only the resampling rules and the horizon unit change. Weekly granularity cannot
  express within-week stock-outs, which is accepted for the prototype.

### ADR-5 Forecast runs execute in the background

- Status: Proposed (2026-10-18); to be confirmed against NFR-01 with the first models in
  November 2026.
- Context: a forecast run over the whole catalogue can take minutes, which is far beyond
  an acceptable HTTP request duration (NFR-02 requires typical pages within 2 seconds).
  Runs must be observable, repeatable and must not corrupt data when they fail.
- Decision: `POST /api/v1/forecast-runs` only creates a `forecast_run` row with status
  `queued` and returns immediately; a background job runner inside the backend process
  executes runs one at a time, updates `status` (`queued`, `running`, `completed`,
  `failed`) with `started_at` and `finished_at`, and commits forecasts and risk assessments
  only when the run has completed. Periodic runs (planned: weekly after the import) are
  scheduled by the same runner. The initial implementation is a single worker thread with
  an in-memory queue; an external task queue with separate worker processes is adopted only
  if measurements show that NFR-01 cannot be met in-process.
- Consequences: the API stays responsive during runs, the interface can show progress by
  polling, and failed runs are visible in the audit log and in the Forecast view. A single
  backend replica is assumed; the in-memory queue is lost on restart, `forecast_run` rows
  still in status `queued` are re-queued on start-up, and a run that was `running` when
  the process stopped is marked `failed`. Running the forecasting package inside the API
  process limits isolation, which is the price of the simplicity of ADR-1 and of this
  in-process runner for a three-person team.

## 10. Alignment with requirements

Requirement IDs and priorities are those of `docs/requirements.md`; the wording in the
tables below is abbreviated.

### 10.1 Components → functional requirements

| Component | Covers | Notes |
|---|---|---|
| Imports view, `imports` router, ImportService | FR-01, FR-02, FR-10, FR-17, FR-18 | FR-10 via `planned_receipts.csv`; a dedicated planned-receipts endpoint is proposed for the API contract |
| Items view, `items` router, CatalogueService | FR-03, FR-04, FR-05 | Suppliers and lead times maintained on the item page |
| Forecast view, `forecast-runs` router, ForecastService, background job runner | FR-06, FR-07 | Horizon configurable per run; model information stored in `forecast_run.config_json` |
| Forecasting package (validation, feature preparation, baselines, ML models, evaluation) | FR-06, FR-16, FR-17 | Baselines and metrics as listed in section 4.1; censored-demand handling in feature preparation |
| Risks view, `risks` router, RiskService | FR-08, FR-09, FR-11, FR-13 | Thresholds owned by RiskService; CSV report served by the `risks` router |
| Settings view, `config` router | FR-11, FR-14 | Threshold editing; user and role management for administrators |
| `notifications` router, NotificationService | FR-12 | In-app only |
| `auth` router, AuditService | FR-14, FR-15 | Audit entries for imports, forecast runs, configuration and user changes |
| Dashboard view | FR-09, FR-12 | Summary of risk levels and unread notifications |
| Repositories, PostgreSQL | all | Persistence of every entity |

### 10.2 Functional requirements → components (coverage check)

| ID | Requirement | Priority | Components | Status |
|---|---|---|---|---|
| FR-01 | Import consumption, stock and receipt data from CSV/XLSX files | Must | ImportService, `imports` router, Imports view | Designed |
| FR-02 | Validate imported data and report errors: missing columns, negative quantities, unknown items, duplicate periods | Must | ImportService validation rules, Imports view | Designed |
| FR-03 | Maintain the medicine catalogue: code, name, unit, group, active flag | Must | CatalogueService, `items` router, Items view | Designed |
| FR-04 | Maintain suppliers and lead times per item | Should | CatalogueService, Items view | Designed; API endpoints to be added to the contract |
| FR-05 | View current stock and consumption history per item as table and chart | Must | `items` router (`/history`), Items view (table and chart) | Designed |
| FR-06 | Run a forecast for all or selected items for a configurable horizon | Must | `forecast-runs` router, ForecastService, job runner, forecasting package | Designed |
| FR-07 | View the forecast per item together with history, point forecast, interval and model information | Must | `items` router (`/forecast`), Forecast view | Designed |
| FR-08 | Calculate shortage risk per item from forecast, current stock, planned receipts and lead time | Must | RiskService | Designed |
| FR-09 | Show a prioritised list of items at risk with risk level and expected stock-out date | Must | `risks` router, Risks view, Dashboard view | Designed |
| FR-10 | Record planned deliveries (expected receipts) | Should | ImportService (`planned_receipts.csv`), `planned_receipt` entity | Designed; manual-entry endpoint proposed |
| FR-11 | Configure risk thresholds and safety-stock parameters | Should | `config` router, RiskService, Settings view | Designed |
| FR-12 | Generate in-app notifications for high-risk items | Should | NotificationService, `notifications` router, Dashboard view | Designed |
| FR-13 | Export forecast and risk reports to CSV/XLSX | Should | `risks` router (`/reports/risks.csv`) | Designed for CSV; XLSX and forecast report planned |
| FR-14 | Authenticate users and manage roles: administrator, pharmacist, viewer | Must | `auth` router, role dependencies, Settings view | Designed |
| FR-15 | Keep an audit log of imports, forecast runs and configuration changes | Should | AuditService | Designed |
| FR-16 | Compare forecasting models against baselines on a hold-out period and show MAE and WAPE | Should | Forecasting evaluation, `forecasting/experiments/`; presentation in the Forecast view | Designed; UI presentation to be detailed |
| FR-17 | Flag stock-out periods so that zero consumption during a stock-out is treated as censored demand | Must | ImportService (`is_stock_out`), forecasting feature preparation | Designed |
| FR-18 | Show a data-quality summary per import: coverage, gaps, outliers | Should | ImportService (`summary_json`), Imports view | Designed |

### 10.3 Non-functional requirements → architectural mechanisms

| ID | Requirement | Priority | Mechanism | Verification |
|---|---|---|---|---|
| NFR-01 | A forecast run for 1,000 items with 3 years of weekly history completes within 5 minutes on a 4 vCPU / 8 GB server | Should | In-process package (ADR-1), background run (ADR-5), vectorised baselines and global ML models | Timed run on the synthetic dataset (`docs/verification-and-evaluation-plan.md`) |
| NFR-02 | Typical pages respond within 2 seconds with up to 5,000 items | Should | Purpose-built endpoints, indexes on `(item_id, period_start)`, pagination of lists | Response-time measurement in integration testing |
| NFR-03 | Role-based access control; passwords stored hashed; HTTPS in deployment | Must | Section 8.1; reverse proxy for TLS | Backend tests for permissions; deployment checklist |
| NFR-04 | No patient personal data is stored or processed | Must | Entity model contains no patient entities; import formats carry item-level data only | Review of schema and import formats |
| NFR-05 | Forecast experiments are reproducible: fixed seeds, versioned configurations, saved results | Must | `forecast_run.config_json`, fixed seeds, versioned configurations in `forecasting/experiments/` | Re-run of a saved configuration yields identical results |
| NFR-06 | The forecasting module rejects malformed input with a clear error instead of producing a wrong forecast | Must | `forecasting.data.validation`; typed exceptions surfaced as failed runs | Unit tests with malformed inputs |
| NFR-07 | Deployable with Docker Compose on Linux with documented setup | Should | Section 7 | Fresh deployment following the documented setup |
| NFR-08 | Automated tests for backend and forecasting run in CI on every pull request | Must | GitHub Actions workflow with pytest and frontend build | CI status on pull requests |
| NFR-09 | UI works in current Chrome, Firefox and Edge on desktop, responsive down to 1280 px | Should | SPA with responsive layout | Manual check during user testing |
| NFR-10 | Interface in English first; Russian localisation planned | Could | UI strings kept in message files from the start | Planned |

## 11. Next steps for this document

- Confirm ADR-5 (background run mechanism) with a timed run of the first models on the
  synthetic dataset (November 2026).
- Add the planned-receipts and supplier endpoints to `docs/architecture/api-contract.md`
  (FR-04, FR-10) and reflect them in section 4.1.
- Produce the SVG exports of both diagrams from the Mermaid sources and review the
  document with the team and the supervisor before the `pre-defense-1` tag.
