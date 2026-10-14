# PharmaStock

*Task PHA2-1 · Last updated: 2026-10-14*

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

Patients are not users of the system, and **no patient data is processed** (see NFR-04 in the requirements specification).

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

The team composition, roles, plan and evaluation methodology were approved by the supervisor in a justification letter dated 9 October 2026. The team meets the supervisor weekly; individual contribution is tracked by tasks, commits and demos. The detailed allocation of responsibilities is kept in [docs/project-management/responsibilities.md](docs/project-management/responsibilities.md) (planned).

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
| Data source | Real data from a partner healthcare organization is being requested (project risk); a documented synthetic dataset is used for development until real data are available |
| Forecast quality | MAE and WAPE (WAPE only when total actual consumption in the window > 0) against naive, seasonal-naive, moving-average and Croston/SBA baselines; time-based train/validation/test split |
| Alert quality | Precision and recall of shortage alerts against actual stock-outs on the test period |

## Current development status

**As of 14 October 2026 the project is at the analysis and design stage.**

| Area | Status |
|---|---|
| Repository | Initialised on GitHub (`birxnm/diploma-pharmacy`, default branch `main`) |
| Team, roles, plan, evaluation methodology | Approved by the supervisor (9 October 2026) |
| Forecasting module concept | Described in [forecasting/README.md](forecasting/README.md) |
| Project documentation for pre-defense 1 | In progress: proposal, evidence of relevance, literature review, existing systems and technology comparison, requirements, architecture and diagrams, UX mockups, data specification, verification and evaluation plan, project management documents |
| Application code (backend, forecasting package, frontend) | Not started; scaffolds are planned for the remainder of October 2026 |
| Next checkpoint | Pre-defense 1 materials due 24 October 2026 (Git tag `pre-defense-1`) |

## Selected technologies

The technology decisions below are fixed for the project. The comparison of alternatives and the reasoning behind each choice are documented in [docs/technology-comparison.md](docs/technology-comparison.md) (planned); the "Why" column gives only a one-line pointer.

| Area | Technology | Why (details in docs/technology-comparison.md) |
|---|---|---|
| Backend language and framework | Python 3.12, FastAPI, Pydantic v2, uvicorn | Same language as the forecasting module, so forecasts are called in-process; typed request/response models and generated API documentation |
| Data access and migrations | SQLAlchemy 2.x, Alembic | Typed ORM models that mirror the data entities; versioned schema migrations |
| Database | PostgreSQL 16 | Relational data with time series per item, JSON columns for configuration and summaries, runs locally in Docker |
| Forecasting | pandas, numpy, scikit-learn, statsforecast, LightGBM | Standard tabular time-series toolchain; statsforecast covers the intermittent-demand baselines (Croston/SBA), LightGBM is the ML candidate |
| Frontend | Vue 3, Vite, TypeScript, Vue Router, Pinia, Chart.js | Component-based SPA for dashboards and item pages; Chart.js for history, forecast and interval charts |
| Infrastructure | Docker Compose (PostgreSQL), GitHub Actions CI | Reproducible local environment; automated tests on every pull request (NFR-08) |
| Tests | pytest (backend, forecasting); Vitest (frontend, later) | Standard test runners for each stack |
| Documentation | Markdown with Mermaid diagrams | Rendered directly on GitHub; diagram sources are editable text files |
| Task tracking | [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b) | Required by the university; task IDs are referenced in branches and pull requests |

## Project documentation and task tracking

**Task tracking:** [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b). Task IDs have the form `PHA2-<n>`.

All project documentation lives in [docs/](docs/) with [docs/README.md](docs/README.md) as the index. Documents marked *planned* are not yet in the repository; the links will work once the corresponding task is merged. Status is as of 14 October 2026.

| Area | Document | Status |
|---|---|---|
| Index | [docs/README.md](docs/README.md) | planned |
| Project proposal | [docs/proposal.md](docs/proposal.md) | planned |
| Evidence of relevance | [docs/evidence-of-relevance/stakeholders.md](docs/evidence-of-relevance/stakeholders.md) | planned |
| Evidence of relevance | [docs/evidence-of-relevance/interview-guide.md](docs/evidence-of-relevance/interview-guide.md) | planned |
| Evidence of relevance | [docs/evidence-of-relevance/interview-log.md](docs/evidence-of-relevance/interview-log.md) | planned |
| Literature review | [docs/literature-review.md](docs/literature-review.md) | planned |
| Existing systems comparison | [docs/existing-systems-comparison.md](docs/existing-systems-comparison.md) | planned |
| Technology comparison | [docs/technology-comparison.md](docs/technology-comparison.md) | planned |
| Requirements specification | [docs/requirements.md](docs/requirements.md) | planned |
| Architecture | [docs/architecture/architecture.md](docs/architecture/architecture.md) | planned |
| Architecture | [docs/architecture/api-contract.md](docs/architecture/api-contract.md) | planned |
| Architecture | [docs/architecture/database-schema.md](docs/architecture/database-schema.md) | planned |
| Diagrams (editable sources) | [docs/diagrams/src/](docs/diagrams/src/) (`*.mmd`, Mermaid) | planned |
| Diagrams (exports) | [docs/diagrams/export/](docs/diagrams/export/) (`*.svg`) | planned |
| UX | [docs/ux/user-scenarios.md](docs/ux/user-scenarios.md) | planned |
| UX | [docs/ux/use-cases.md](docs/ux/use-cases.md) | planned |
| UX prototype | [prototype/](prototype/) (static HTML/CSS mockups of key screens) | planned |
| Data | [docs/data/data-specification.md](docs/data/data-specification.md) | planned |
| Verification and evaluation plan | [docs/verification-and-evaluation-plan.md](docs/verification-and-evaluation-plan.md) | planned |
| Project management | [docs/project-management/plan-and-milestones.md](docs/project-management/plan-and-milestones.md) | planned |
| Project management | [docs/project-management/risks.md](docs/project-management/risks.md) | planned |
| Project management | [docs/project-management/responsibilities.md](docs/project-management/responsibilities.md) | planned |
| Project management | [docs/project-management/task-register.md](docs/project-management/task-register.md) | planned |
| Supervision | [docs/supervision/feedback-log.md](docs/supervision/feedback-log.md) | planned |
| Forecasting module | [forecasting/README.md](forecasting/README.md) | available |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) | available |

## Repository structure

Target layout of the repository. As of 14 October 2026 the repository contains `README.md`, `CONTRIBUTING.md`, the documentation index in `docs/README.md` and `forecasting/README.md`; the remaining directories and files are added as the corresponding `PHA2-<n>` tasks are completed.

```
.
├── README.md                      # this file
├── CONTRIBUTING.md                # branching, pull requests, review, commit messages
├── .gitignore
├── .env.example                   # configuration example with placeholder values
├── docker-compose.yml             # PostgreSQL for local development
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/ci.yml           # backend and forecasting tests on every pull request
├── backend/                       # FastAPI service (Abzal)
│   ├── app/
│   │   ├── main.py
│   │   ├── core/config.py
│   │   ├── api/routes/            # REST API v1 routes
│   │   └── db/models.py           # SQLAlchemy models of the data entities
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── forecasting/                   # forecasting package (Evelina)
│   ├── forecasting/
│   │   ├── data/                  # schema.py, validation.py
│   │   ├── models/                # baselines.py
│   │   ├── evaluation/            # metrics.py, split.py
│   │   └── api.py                 # forecast_items(history, horizon, config)
│   ├── data/                      # generate_synthetic.py, sample/*.csv
│   ├── experiments/               # configs and saved results per run
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── frontend/                      # Vue 3 + Vite application (Birkhanym)
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
├── prototype/                     # static HTML/CSS mockups of key screens
└── docs/                          # project documentation (see table above)
    ├── README.md                  # documentation index
    ├── proposal.md
    ├── evidence-of-relevance/
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
    ├── project-management/        # plan-and-milestones.md, risks.md, responsibilities.md, task-register.md
    └── supervision/               # feedback-log.md
```

Raw and processed datasets are not committed. Secrets (passwords, API keys) are never committed; configuration is provided through `.env` files based on `.env.example`.

## Setup, execution and testing

Runnable code is not yet in the repository (status as of 14 October 2026). As soon as the first runnable components are merged, this section will be extended with:

- **Setup:** prerequisites, how to start PostgreSQL with Docker Compose, how to install the backend, forecasting and frontend dependencies, and how to configure the environment from `.env.example`.
- **Execution:** how to start the backend API, run a forecast and open the web interface.
- **Testing:** how to run the backend and forecasting test suites locally; the same suites run in GitHub Actions on every pull request.

Each component will also carry its own README (`backend/README.md`, `forecasting/README.md`, `frontend/README.md`) with component-specific instructions. The planned data preparation and modelling pipeline is already described in [forecasting/README.md](forecasting/README.md).

## Milestones

From the plan approved by the supervisor. Detailed planning is kept in [docs/project-management/plan-and-milestones.md](docs/project-management/plan-and-milestones.md) (planned).

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

- Every meaningful work item is a Linear issue `PHA2-<n>` with a responsible student, expected outcome, acceptance criteria and deadline.
- `main` is the reviewed baseline. Work is done in branches named `PHA2-<n>-<slug>` and merged through pull requests that reference the task and describe how the change was checked.
- Another team member reviews every pull request before merging.
- Documentation and design changes are committed the same way as code.
- Each member commits from their own account with identifiable author details.

The full conventions (branching, commit messages, pull request template, review checklist) are described in [CONTRIBUTING.md](CONTRIBUTING.md) (planned).
