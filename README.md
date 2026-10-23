# PharmaStock

*Task PHA2-1 (updates PHA2-1) · Last updated: 2026-10-20*

**Development of smart supply chain analytics system for forecasting pharmaceutical inventory and preventing medicine shortages in healthcare organizations**

Diploma project · Astana IT University · School of Software Engineering · Educational program Software Engineering · Group SE-2414 · Academic year 2026–2027

PharmaStock is a prototype web system for hospital and polyclinic pharmacies. It imports consumption, stock and receipt data from the exports of existing accounting systems, forecasts weekly consumption per medicine item, and combines the forecast with current stock, expected deliveries and supplier lead time into an early shortage-risk signal. Pharmacy staff get a prioritised list of items at risk with the expected stock-out date, item pages with history and forecast, in-app notifications and exportable reports.

## Contents

- [Problem statement](#problem-statement)
- [Target users](#target-users)
- [Aim and objectives](#aim-and-objectives)
- [Expected outcomes](#expected-outcomes)
- [Team and supervisor](#team-and-supervisor)
- [Project scope](#project-scope)
- [Current development status](#current-development-status)
- [Selected technologies](#selected-technologies)
- [Project documentation and task tracking](#project-documentation-and-task-tracking)
- [Repository structure](#repository-structure)
- [Setup, execution and testing](#setup-execution-and-testing)
- [Milestones](#milestones)
- [How we work](#how-we-work)

## Problem statement

Healthcare organizations (hospitals, polyclinics) in Kazakhstan manage pharmacy stock mostly with accounting systems and spreadsheets. These tools record what has happened but do not say what is likely to happen next:

- Medicine consumption is **intermittent**: long runs of zero demand with occasional spikes, which makes simple averages unreliable.
- **Lead times are long.** A large part of the stock is procured centrally through the single distributor SK-Pharmacy for the guaranteed volume of free medical care; the rest is bought by the organization itself. An order placed after the shelf is empty arrives too late.
- **Shortages are discovered late**, while other items are overstocked and expire.
- Zero consumption during a stock-out looks like zero demand in the records, although the demand was there and simply could not be met.

Pharmacy staff lack a tool that forecasts consumption per item and turns forecasts, current stock, expected deliveries and lead time into an early shortage-risk signal. PharmaStock is intended to fill this gap.

## Target users

| User | Role in the system |
|---|---|
| Head of hospital pharmacy / pharmacist (primary) | Imports data, runs forecasts, reviews the risk list and item pages, configures thresholds and safety stock |
| Procurement and supply specialist | Uses the risk list and expected stock-out dates to plan purchases; records planned deliveries |
| Heads of clinical departments | View only: stock, forecasts and risks for the items they use |
| System administrator | Manages users and roles, reviews the audit log |

Patients are not users of the system, and **no patient data is processed** (see NFR-04 in the [requirements specification](docs/requirements.md)).

## Aim and objectives

**Aim:** develop a prototype of a smart supply chain analytics system that forecasts pharmaceutical consumption and warns about shortage risk in healthcare organizations.

**Objectives:**

1. Analyse the domain, existing systems and literature.
2. Define requirements and architecture.
3. Prepare data and build forecasting models compared with baselines.
4. Implement backend, database, API and risk calculation.
5. Implement the web interface.
6. Evaluate the system on a hold-out period and with users.
7. Document results and prepare a scientific article.

## Expected outcomes

- A working prototype: backend + PostgreSQL + forecasting module + web UI.
- A comparison of forecasting models against baselines (naive, seasonal-naive, moving-average, Croston/SBA) using MAE and WAPE on a hold-out period.
- Error analysis per medicine group and a description of limitations.
- Technical documentation, thesis text and a scientific article.

## Team and supervisor

| Team member | GitHub | Responsibilities |
|---|---|---|
| Birkhanym Kazhymukhamet | [@birxnm](https://github.com/birxnm) | Requirements analysis and user scenarios, web interface (frontend), UX mockups, visualisation of forecasts and shortage alerts, user testing |
| Abzal Bakhytov | to be added | Backend (Python), database, REST API, data import and validation, integration of the forecasting module, shortage-risk calculation, access control and audit log, deployment and API documentation |
| Evelina Penkova | [@etoevelina](https://github.com/etoevelina) | Data preparation and analysis, forecasting models (baselines and ML), hyperparameter tuning, evaluation on a hold-out period, error analysis, reproducible experiments, serving forecasts through the API together with Abzal |

**Supervisor:** Kuralay Makhmetova, Senior Lecturer, School of Software Engineering, Astana IT University.

The team composition, roles, plan and evaluation methodology were approved by the supervisor in a justification letter dated 9 October 2026. The team meets the supervisor weekly; individual contribution is tracked by tasks, commits and demos. The detailed allocation of responsibilities (RACI per work area, ownership of repository parts, thesis chapters) is kept in [docs/project-management/responsibilities.md](docs/project-management/responsibilities.md); supervisor feedback and the decisions taken in response are recorded in [docs/supervision/feedback-log.md](docs/supervision/feedback-log.md).

## Project scope

### In scope

- Import of consumption, stock and receipt data from CSV/XLSX exports.
- Medicine catalogue; suppliers and lead times per item.
- Weekly consumption forecast per item for a configurable horizon (initial decision: weekly step, 12-week horizon).
- Shortage-risk calculation from forecast, current stock, planned receipts and lead time.
- Prioritised risk list with risk level and expected stock-out date; in-app notifications.
- Dashboards and item pages with history, forecast and interval.
- Configuration of risk thresholds and safety stock.
- Users and roles (administrator, pharmacist, viewer); audit log.
- Export of forecast and risk reports.
- Comparison of forecasting models against baselines on hold-out data.

### Out of scope

- Ordering and procurement execution.
- Electronic prescriptions.
- Real-time integration with national systems and 1C (future work).
- Mobile application.
- Patient data of any kind.
- Multi-organization SaaS.

### Key initial decisions (open for revision during requirements analysis)

| Decision | Current choice |
|---|---|
| Time step and horizon | Weekly step, 12-week horizon |
| Data history | Consumption, stock levels and receipts per item |
| Stock-outs | Zero consumption during a stock-out is censored demand: it is flagged, not learned as zero |
| Data source | Real data from a partner healthcare organization is being requested (project risk, task PHA2-26); a documented synthetic dataset is used for development until real data are available |
| Forecast quality | MAE and WAPE (WAPE only when total actual consumption in the window > 0) against naive, seasonal-naive, moving-average and Croston/SBA baselines; time-based train/validation/test split |
| Alert quality | Precision and recall of shortage alerts against actual stock-outs on the test period |

## Current development status

**As of 20 October 2026 the analysis and design stage is complete, the first runnable components are in the repository, and the project is being packaged for pre-defense 1 (materials due 24 October 2026, Git tag `pre-defense-1`).**

| Area | Status (20 October 2026) |
|---|---|
| Project documentation for pre-defense 1 | **Complete and merged:** proposal, evidence of relevance (stakeholders, interview guide, interview log template), literature review, existing systems comparison, technology comparison, requirements specification (FR-01…FR-18, NFR-01…NFR-10), architecture with system context and component diagrams, database schema with ER diagram, REST API contract, user scenarios and use cases with use case diagram, data specification, verification and evaluation plan, project management documents (plan and milestones, risks, responsibilities, task register), supervisor feedback log |
| UX mockups | **Merged:** seven static HTML/CSS screens in [prototype/](prototype/) (dashboard, risks, catalogue, item page, forecast runs, imports, settings) mapped to the functional requirements |
| Backend scaffold | **Merged, tests pass:** FastAPI application factory and settings, `GET /api/v1/health`, SQLAlchemy models of the catalogue and the imported time series (`medicine_item`, `supplier`, `item_supplier`, `import_batch`, `consumption_record`, `stock_snapshot`, `receipt`, `planned_receipt`), Alembic configured (no migration files yet), PostgreSQL 16 in Docker Compose, `.env.example`; 21 tests |
| Forecasting package | **Merged, tests pass:** input schema and validation (malformed input is rejected with a clear error, NFR-06), regular weekly series with stock-out flags, baselines `naive`, `seasonal_naive` (season 52), `moving_average(window)`, `croston`, `sba`, metrics `mae`, `wape` (`None` when the sum of actuals is 0), `bias`, rolling-origin time-based split, entry point `forecasting.api.forecast_items(history, horizon, config)`; 188 tests |
| Synthetic development dataset | **Merged:** deterministic generator `forecasting/data/generate_synthetic.py` and a committed sample (20 items, 104 weeks, seed 42) in the four import formats, with stock-out weeks and censored demand |
| Frontend scaffold | **In review (PHA2-23):** Vue 3 + Vite + TypeScript with Vue Router, Pinia, typed API client, placeholder views and unit tests |
| Continuous integration | **In review (PHA2-22):** GitHub Actions workflow running the backend and forecasting test suites on every pull request (NFR-08) |
| Experiment runner | **In review (PHA2-24):** versioned configuration and runner for the baseline comparison in `forecasting/experiments/` |
| Not started | REST API v1 endpoints beyond health (authentication, items, imports, forecast runs, risks, notifications, thresholds, reports), shortage-risk calculation, machine-learning models (first comparison planned as PHA2-27), user interviews (PHA2-25), real data access (PHA2-26) |

What runs today from a clean clone: the backend health endpoint and its interactive API documentation, both Python test suites, the synthetic data generator, forecasting of the sample data with the baselines from Python, and the static mockups. See [Setup, execution and testing](#setup-execution-and-testing). The task-level view of this status is kept in [docs/project-management/task-register.md](docs/project-management/task-register.md).

## Selected technologies

The technology decisions below are fixed for the project. The comparison of alternatives and the reasoning behind each choice are documented in [docs/technology-comparison.md](docs/technology-comparison.md); the "Why" column gives only a one-line pointer.

| Area | Technology | Why (details in docs/technology-comparison.md) |
|---|---|---|
| Backend language and framework | Python 3.12, FastAPI, Pydantic v2, uvicorn | Same language as the forecasting module, so forecasts are called in-process; typed request/response models and generated API documentation |
| Data access and migrations | SQLAlchemy 2.x, Alembic | Typed ORM models that mirror the data entities; versioned schema migrations |
| Database | PostgreSQL 16 | Relational data with time series per item, JSON columns for configuration and summaries, runs locally in Docker |
| Forecasting | pandas, numpy, scikit-learn, statsforecast, LightGBM | Standard tabular time-series toolchain; statsforecast covers the intermittent-demand baselines (Croston/SBA), LightGBM is the ML candidate. The baselines currently in the package are own implementations on pandas and numpy, checked against hand-computed values; statsforecast and LightGBM enter the dependencies with the candidate models (PHA2-27) |
| Frontend | Vue 3, Vite, TypeScript, Vue Router, Pinia, Chart.js | Component-based SPA for dashboards and item pages; Chart.js for history, forecast and interval charts |
| Infrastructure | Docker Compose (PostgreSQL), GitHub Actions CI | Reproducible local environment; automated tests on every pull request (NFR-08) |
| Tests | pytest (backend, forecasting); Vitest (frontend) | Standard test runners for each stack |
| Documentation | Markdown with Mermaid diagrams | Rendered directly on GitHub; diagram sources are editable text files |
| Task tracking | [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b) | Required by the university; task IDs are referenced in branches and pull requests |

## Project documentation and task tracking

**Task tracking:** [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b). Task IDs have the form `PHA2-<n>`; the register of all tasks with responsible member, acceptance criteria, deadline and status is mirrored in [docs/project-management/task-register.md](docs/project-management/task-register.md).

All project documentation lives in [docs/](docs/) with [docs/README.md](docs/README.md) as the index. Status is as of 20 October 2026: *available* means merged into `main`; *in review* means the pull request is open.

| Area | Document | Status |
|---|---|---|
| Index | [docs/README.md](docs/README.md) | available |
| Project proposal | [docs/proposal.md](docs/proposal.md) | available |
| Evidence of relevance | [docs/evidence-of-relevance/stakeholders.md](docs/evidence-of-relevance/stakeholders.md) | available |
| Evidence of relevance | [docs/evidence-of-relevance/interview-guide.md](docs/evidence-of-relevance/interview-guide.md) | available |
| Evidence of relevance | [docs/evidence-of-relevance/interview-log.md](docs/evidence-of-relevance/interview-log.md) | available (template; interviews planned as PHA2-25) |
| Literature review | [docs/literature-review.md](docs/literature-review.md) | available |
| Existing systems comparison | [docs/existing-systems-comparison.md](docs/existing-systems-comparison.md) | available |
| Technology comparison | [docs/technology-comparison.md](docs/technology-comparison.md) | available |
| Requirements specification | [docs/requirements.md](docs/requirements.md) | available |
| Architecture | [docs/architecture/architecture.md](docs/architecture/architecture.md) | available |
| Architecture | [docs/architecture/api-contract.md](docs/architecture/api-contract.md) | available |
| Architecture | [docs/architecture/database-schema.md](docs/architecture/database-schema.md) | available |
| Diagrams (editable sources) | [docs/diagrams/src/](docs/diagrams/src/): `system-context.mmd`, `component-diagram.mmd`, `er-diagram.mmd`, `use-case-diagram.mmd` | available |
| Diagrams (exports) | [docs/diagrams/export/](docs/diagrams/export/) (`*.svg`, see [docs/diagrams/README.md](docs/diagrams/README.md)) | available |
| UX | [docs/ux/user-scenarios.md](docs/ux/user-scenarios.md) | available |
| UX | [docs/ux/use-cases.md](docs/ux/use-cases.md) | available |
| UX prototype | [prototype/README.md](prototype/README.md) (static HTML/CSS mockups of key screens) | available |
| Data | [docs/data/data-specification.md](docs/data/data-specification.md) | available |
| Data | [forecasting/data/README.md](forecasting/data/README.md) (synthetic dataset and generator) | available |
| Verification and evaluation plan | [docs/verification-and-evaluation-plan.md](docs/verification-and-evaluation-plan.md) | available |
| Project management | [docs/project-management/plan-and-milestones.md](docs/project-management/plan-and-milestones.md) | available |
| Project management | [docs/project-management/risks.md](docs/project-management/risks.md) | available |
| Project management | [docs/project-management/responsibilities.md](docs/project-management/responsibilities.md) | available |
| Project management | [docs/project-management/task-register.md](docs/project-management/task-register.md) | available |
| Project management | [docs/project-management/ci.md](docs/project-management/ci.md) (what CI checks and how to run the same checks locally) | in review (PHA2-22) |
| Supervision | [docs/supervision/feedback-log.md](docs/supervision/feedback-log.md) | available |
| Forecasting module | [forecasting/README.md](forecasting/README.md) (approach: data assumptions, baselines, metrics, split, reproducibility) | available |
| Forecasting experiments | [forecasting/experiments/README.md](forecasting/experiments/README.md) | in review (PHA2-24) |
| Backend | [backend/README.md](backend/README.md) | available |
| Frontend | [frontend/README.md](frontend/README.md) | in review (PHA2-23) |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) | available |

## Repository structure

Layout of the repository as of 20 October 2026. Directories marked *in review* exist on task branches with an open pull request and are merged into `main` once reviewed.

```
.
├── README.md                      # this file
├── CONTRIBUTING.md                # tasks, branching, commit messages, pull requests, review, tags
├── .gitignore
├── .env.example                   # configuration template with placeholder values (copy to .env)
├── docker-compose.yml             # PostgreSQL 16 service "db" for local development
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/ci.yml           # backend and forecasting tests on every pull request (in review)
├── backend/                       # FastAPI service (Abzal)
│   ├── app/
│   │   ├── main.py                # create_app() factory and the ASGI object `app`
│   │   ├── core/config.py         # settings read from environment variables / .env
│   │   ├── api/routes/health.py   # GET /api/v1/health (further routes follow per task)
│   │   └── db/                    # base.py, models.py (data entities), session.py
│   ├── alembic/                   # migration environment; alembic/versions/ is empty so far
│   ├── alembic.ini
│   ├── tests/                     # test_health.py, test_session.py, test_models.py
│   ├── pyproject.toml             # dependencies, "dev" extra, pytest configuration
│   └── README.md
├── forecasting/                   # forecasting package (Evelina)
│   ├── forecasting/               # importable package
│   │   ├── data/                  # schema.py, validation.py
│   │   ├── models/                # baselines.py
│   │   ├── evaluation/            # metrics.py, split.py
│   │   └── api.py                 # forecast_items(history, horizon, config)
│   ├── data/
│   │   ├── generate_synthetic.py  # deterministic synthetic dataset generator
│   │   ├── sample/                # committed sample: consumption, stock, receipts, planned_receipts, items, dataset.json
│   │   └── README.md
│   ├── experiments/               # configs/, run_baselines.py, results/ (in review)
│   ├── tests/                     # test_validation.py, test_baselines.py, test_metrics.py, test_split.py, test_api.py
│   ├── pyproject.toml             # dependencies, "dev" extra, pytest configuration
│   └── README.md                  # approach of the forecasting module
├── frontend/                      # Vue 3 + Vite application (Birkhanym) (in review)
│   ├── src/                       # main.ts, App.vue, api/, stores/, router/, components/, views/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── prototype/                     # static HTML/CSS mockups of key screens (Birkhanym)
│   ├── index.html                 # dashboard; risks.html, items.html, item.html, forecast.html, imports.html, settings.html
│   ├── styles.css
│   └── README.md
└── docs/                          # project documentation (see table above)
    ├── README.md                  # documentation index
    ├── proposal.md
    ├── evidence-of-relevance/     # stakeholders.md, interview-guide.md, interview-log.md
    ├── literature-review.md
    ├── existing-systems-comparison.md
    ├── technology-comparison.md
    ├── requirements.md
    ├── architecture/              # architecture.md, api-contract.md, database-schema.md
    ├── diagrams/
    │   ├── src/                   # *.mmd (editable Mermaid sources)
    │   └── export/                # *.svg (readable exports)
    ├── ux/                        # user-scenarios.md, use-cases.md
    ├── data/                      # data-specification.md
    ├── verification-and-evaluation-plan.md
    ├── project-management/        # plan-and-milestones.md, risks.md, responsibilities.md, task-register.md, ci.md (in review)
    └── supervision/               # feedback-log.md
```

Raw and processed datasets are not committed; only the small documented sample under `forecasting/data/sample/` is tracked. Secrets (passwords, API keys) are never committed; configuration is provided through a `.env` file based on `.env.example`. Experiment run directories under `forecasting/experiments/results/` are produced locally and are not committed either.

## Setup, execution and testing

The commands below were checked on 20 October 2026 on macOS with Python 3.12 and Docker Compose; the Python commands are the same ones the CI workflow runs. Each component also has its own README with more detail: [backend/README.md](backend/README.md), [forecasting/data/README.md](forecasting/data/README.md), [prototype/README.md](prototype/README.md), [frontend/README.md](frontend/README.md) (in review).

### Prerequisites

| Tool | Needed for | Notes |
|---|---|---|
| Git | everything | — |
| Python 3.12 | backend, forecasting | both packages declare `requires-python >= 3.12` |
| Docker with the Compose plugin | PostgreSQL | optional at this stage: the health endpoint and all tests run without a database |
| Node.js 20 or newer with npm 10 | frontend (in review) | not needed for the backend, the forecasting package or the mockups |
| A current desktop browser (Chrome, Firefox or Edge) | mockups, API documentation, frontend | NFR-09 |

### 1. Clone and configure

```bash
git clone https://github.com/birxnm/diploma-pharmacy.git
cd diploma-pharmacy
cp .env.example .env        # then replace the placeholder values
```

`.env` is read by Docker Compose (database user, password, name and port) and by the backend (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, …). It is ignored by Git. Every backend setting has a development default, so the backend and its tests also start without `.env`; Docker Compose refuses to start without the `POSTGRES_*` variables.

### 2. Python environment

One virtual environment in the repository root serves both Python packages. Each package is installed in editable mode with its `dev` extra (pytest and, for the backend, the HTTP test client):

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e "./backend[dev]" -e "./forecasting[dev]"
```

To install only one of the packages, run `pip install -e ".[dev]"` inside `backend/` or `forecasting/` instead; this is what the CI workflow does per job.

### 3. Database (PostgreSQL 16 with Docker Compose)

```bash
docker compose up -d db          # start PostgreSQL 16 in the background
docker compose ps                # the db service must report "healthy"
docker compose logs -f db        # follow the database log
docker compose down              # stop; add -v to delete the data volume as well
```

The service publishes port `${POSTGRES_PORT}` (default 5432) on the host; the backend connects through `DATABASE_URL` from `.env`. To open a `psql` shell inside the container: `docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"`. Schema migrations are managed with Alembic from `backend/` (`alembic upgrade head`); no migration files exist yet, so this step is not required for the current scaffold. If port 5432 is already in use, change `POSTGRES_PORT` and the port in `DATABASE_URL` in `.env`.

### 4. Backend (FastAPI)

Run the API from `backend/`:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- Health check: <http://localhost:8000/api/v1/health> returns `{"status": "ok", "app_name": "PharmaStock", "version": "0.1.0", "environment": "development"}`.
- Interactive API documentation: <http://localhost:8000/docs> (Swagger UI) and <http://localhost:8000/redoc>; OpenAPI document at `/api/v1/openapi.json`.
- The health endpoint does not touch the database, so it works whether or not the `db` service is running. The remaining endpoints of REST API v1 are specified in [docs/architecture/api-contract.md](docs/architecture/api-contract.md) and are implemented task by task.

Tests (FastAPI `TestClient`, in-memory SQLite for the model and session tests; no PostgreSQL or `.env` needed):

```bash
cd backend
pytest -q
```

### 5. Forecasting package

Tests (baselines are checked against hand-computed values; validation tests cover the error cases of NFR-06):

```bash
cd forecasting
pytest -q
```

Synthetic development dataset. The generator is deterministic: the command below reproduces the committed sample byte for byte, so `git status` must stay clean after it. Run it from the repository root:

```bash
python forecasting/data/generate_synthetic.py --items 20 --weeks 104 --seed 42 --out forecasting/data/sample
python forecasting/data/generate_synthetic.py --help      # --items, --weeks, --seed, --out, --end, --write-truth, --omit-zero-rows
python forecasting/data/generate_synthetic.py             # default development set (30 items, 3 years) into ./synthetic, ignored by Git
```

Forecasting from Python, with the package installed as in step 2 (from the repository root):

```python
import pandas as pd
from forecasting.api import forecast_items

history = pd.read_csv("forecasting/data/sample/consumption.csv")
result = forecast_items(history, horizon=12, config={"model": "sba", "params": {"alpha": 0.1}})
result.forecasts    # item_code, period_start, point, model: one row per item and forecast week
result.item_info    # per item: history length, filled weeks, censored weeks, model used
```

Available model names are `naive`, `seasonal_naive`, `moving_average`, `croston` and `sba`; malformed input raises `DataValidationError` instead of producing a forecast. Experiment configurations and the runner for the baseline comparison live in `forecasting/experiments/` (in review, PHA2-24; see its README once merged).

### 6. UI mockups (prototype)

Open `prototype/index.html` in a desktop browser; the pages link to each other through the left navigation and need no server or build step. To serve the folder instead:

```bash
cd prototype
python -m http.server 8080       # then open http://localhost:8080/
```

### 7. Frontend (in review)

The Vue 3 scaffold of PHA2-23 is used as follows once merged; see [frontend/README.md](frontend/README.md) for details.

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api to the backend on port 8000
npm run build        # type check and production build into dist/
npm run test         # Vitest unit tests
```

### 8. Everything together

For a local demo of the current state, in three terminals from the repository root: `docker compose up -d db` (optional), `cd backend && uvicorn app.main:app --reload --port 8000`, and `cd frontend && npm run dev` (once merged). The sidebar of the frontend shows whether the backend answers; the mockups in `prototype/` show the target screens.

### Test summary

| Suite | Command | Needs | CI job (in review, PHA2-22) |
|---|---|---|---|
| Backend | `cd backend && pytest -q` | Python 3.12, `backend[dev]` installed | `backend-tests` |
| Forecasting | `cd forecasting && pytest -q` | Python 3.12, `forecasting[dev]` installed | `forecasting-tests` |
| Synthetic data | regenerate the sample (step 5); `git status` shows no change | forecasting dependencies | — |
| Frontend | `cd frontend && npm run build && npm run test` | Node.js 20 | planned |

Both Python suites run in CI on every pull request and on every push to `main` once the workflow is merged (NFR-08); the lint job (`ruff`) is advisory. The same checks are listed in the pull request template.

## Milestones

From the plan approved by the supervisor. Detailed planning with exit criteria per milestone is kept in [docs/project-management/plan-and-milestones.md](docs/project-management/plan-and-milestones.md).

| Period | Deliverables |
|---|---|
| October 2026 | Requirements, roles, literature and system review, architecture, DB schema, UI mockups, data availability check, repository, experiment plan, pre-defense 1 materials |
| November–December 2026 | Data preparation, baselines, first models, API and main screens, literature review draft |
| January 2027 | Integration demo end to end |
| February 2027 | Tuning, notifications, replenishment calculations, component tests |
| March 2027 | Final experiments, model comparison, error analysis, integration testing |
| April 2027 | Thesis draft, technical documentation, article manuscript, deployed prototype |
| May–June 2027 | Revisions, presentation, pre-defense and defense |

Each submission is tagged in Git: `pre-defense-1`, `pre-defense-2`, `final-pre-defense`. Tags are never moved or replaced after submission.

## How we work

- Every meaningful work item is a Linear issue `PHA2-<n>` with a responsible student, expected outcome, acceptance criteria and deadline, mirrored in [docs/project-management/task-register.md](docs/project-management/task-register.md).
- `main` is the reviewed baseline. Work is done in branches named `PHA2-<n>-<slug>` and merged through pull requests that reference the task and describe how the change was checked ([.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)).
- Commit messages are written in English as `type(scope): subject [PHA2-<n>]`, for example `docs(readme): update status and setup for pre-defense 1 [PHA2-1]`.
- Another team member reviews every pull request before merging; the owner of the affected area is the preferred reviewer.
- Documentation and design changes are committed the same way as code.
- Each member commits from their own account with identifiable author details.

The full conventions (branching, commit messages, pull request template, review checklist, what must never be committed, tags) are described in [CONTRIBUTING.md](CONTRIBUTING.md).
