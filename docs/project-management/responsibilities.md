# PharmaStock — Responsibilities

_PHA2-20 · Last updated: 2026-10-19 · Author: Evelina Penkova · Reviewer: Birkhanym Kazhymukhamet_

The roles of the three team members were approved by the supervisor on 9 October 2026 and are summarised in [proposal.md](../proposal.md) section 2 and `CONTRIBUTING.md` section 1. This document details them per work area in a RACI table, fixes who owns which part of the repository, allocates the thesis chapters and states how individual contribution is tracked. It is the reference for assigning tasks in the [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b) and for choosing reviewers.

## 1. Team

| Member | GitHub | Role in the project | Primary repository areas |
|---|---|---|---|
| Birkhanym Kazhymukhamet | @birxnm | Requirements analysis and user scenarios, web interface (frontend), UX mockups, visualisation of forecasts and shortage alerts, user testing | `frontend/`, `prototype/`, `docs/ux/`, `docs/evidence-of-relevance/`, `docs/existing-systems-comparison.md`, `docs/supervision/` |
| Abzal Bakhytov | — | Backend (Python), database, REST API, data import and validation, integration of the forecasting module, shortage-risk calculation, access control and audit log, deployment and API documentation | `backend/`, `docker-compose.yml`, `.env.example`, `.github/workflows/`, `docs/architecture/`, `docs/technology-comparison.md` |
| Evelina Penkova | @etoevelina | Data preparation and analysis, forecasting models (baselines and ML), hyperparameter tuning, evaluation on a hold-out period, error analysis, reproducible experiments, serving forecasts through the API together with Abzal | `forecasting/`, `docs/data/`, `docs/literature-review.md`, `docs/verification-and-evaluation-plan.md`, `docs/project-management/` |
| Kuralay Makhmetova (supervisor) | — | Senior Lecturer, School of Software Engineering, Astana IT University: guidance, review at checkpoints, approval of the plan and the evaluation methodology | — |

## 2. RACI legend

| Letter | Meaning |
|---|---|
| **R** | Responsible: does the work; several people can be responsible for one area |
| **A** | Accountable: one person per area; signs off the result, keeps the documents of the area consistent and answers for it at the pre-defenses |
| **C** | Consulted: gives input before the work is finished (two-way) |
| **I** | Informed: told about the result (one-way) |

The supervisor column records where supervisor review is part of the process; "A" in that column marks approvals that only the supervisor can give.

## 3. RACI table

### 3.1 Analysis

| Work area | Birkhanym | Abzal | Evelina | Supervisor | Main artefacts |
|---|---|---|---|---|---|
| Problem statement, aim, objectives, scope (proposal) | R, A | C | C | A (approval) | `docs/proposal.md` |
| Stakeholders, interview guide, interviews, evidence of relevance | R, A | I | I | C | `docs/evidence-of-relevance/*` |
| Literature review (intermittent demand forecasting, pharmaceutical inventory, shortage prediction) | C | I | R, A | C | `docs/literature-review.md` |
| Existing systems comparison | R, A | C | C | I | `docs/existing-systems-comparison.md` |
| Technology comparison and stack decision | C | R, A | C | I | `docs/technology-comparison.md` |

### 3.2 Requirements and design

| Work area | Birkhanym | Abzal | Evelina | Supervisor | Main artefacts |
|---|---|---|---|---|---|
| Requirements specification (FR-01 to FR-18, NFR-01 to NFR-10) | R, A | R | R | C | `docs/requirements.md` |
| User scenarios and use cases | R, A | C | I | C | `docs/ux/*`, `docs/diagrams/src/use-case-diagram.mmd` |
| UX mockups of key screens | R, A | I | I | C | `prototype/` |
| Architecture and diagrams (context, components) | C | R, A | C | C | `docs/architecture/architecture.md`, `docs/diagrams/` |
| Database schema and ER diagram | I | R, A | C | I | `docs/architecture/database-schema.md`, `backend/app/db/models.py` |
| API contract (REST API v1) | C | R, A | R | I | `docs/architecture/api-contract.md` |
| Data specification (import formats, validation rules, stock-out flagging) | I | C | R, A | I | `docs/data/data-specification.md` |
| Forecasting module design and interface `forecast_items(history, horizon, config)` | I | C | R, A | C | `forecasting/README.md`, `forecasting/forecasting/api.py` |

### 3.3 Implementation

| Work area | Birkhanym | Abzal | Evelina | Supervisor | Main artefacts |
|---|---|---|---|---|---|
| Backend service, configuration, REST API endpoints | I | R, A | C | I | `backend/app/` |
| Data import and validation (FR-01, FR-02, FR-18) | I | R, A | C | I | `backend/app/api/routes/imports.py` (planned) |
| Medicine catalogue, suppliers, lead times (FR-03, FR-04) | C | R, A | I | I | `backend/` |
| Integration of the forecasting module into the backend; forecast runs (FR-06) | I | R, A | R | I | `backend/`, `forecasting/forecasting/api.py` |
| Serving forecasts through the API (FR-07) | C | R, A | R | I | `backend/`, `docs/architecture/api-contract.md` |
| Shortage-risk calculation and risk list (FR-08, FR-09) | C | R, A | C | I | `backend/` |
| Planned deliveries, thresholds, notifications, export (FR-10 to FR-13) | C | R, A | I | I | `backend/` |
| Authentication, roles, audit log (FR-14, FR-15, NFR-03) | I | R, A | I | I | `backend/` |
| Deployment: Docker Compose, environment, CI (NFR-07, NFR-08) | I | R, A | C | I | `docker-compose.yml`, `.env.example`, `.github/workflows/ci.yml` |
| Web interface: dashboards, item pages, risk list, imports, settings (FR-05, FR-09, FR-13) | R, A | C | I | I | `frontend/` |
| Visualisation of forecasts and shortage alerts (FR-07, FR-12) | R, A | I | C | I | `frontend/` |
| Data preparation and analysis; synthetic dataset | I | C | R, A | I | `forecasting/data/` |
| Stock-out flagging and censored demand handling (FR-17) | I | C | R, A | C | `forecasting/forecasting/data/` |
| Forecasting baselines and metrics (naive, seasonal_naive, moving_average, croston, sba; mae, wape, bias) | I | I | R, A | C | `forecasting/forecasting/models/`, `forecasting/forecasting/evaluation/` |
| ML models and hyperparameter tuning | I | I | R, A | C | `forecasting/` |
| Reproducible experiments (NFR-05): configurations, seeds, saved results | I | I | R, A | I | `forecasting/experiments/` |
| Model comparison on hold-out data shown in the system (FR-16) | R | R | R, A | I | `forecasting/`, `backend/`, `frontend/` |

### 3.4 Verification and evaluation

| Work area | Birkhanym | Abzal | Evelina | Supervisor | Main artefacts |
|---|---|---|---|---|---|
| Verification and evaluation plan | R | R | R, A | C | `docs/verification-and-evaluation-plan.md` |
| Evaluation of models on the hold-out period (MAE, WAPE); error analysis per medicine group | I | I | R, A | C | `forecasting/experiments/` |
| Precision and recall of shortage alerts against actual stock-outs | I | R | R, A | C | `forecasting/experiments/`, `backend/` |
| Backend unit and integration tests | I | R, A | C | I | `backend/tests/` |
| Forecasting module tests | I | I | R, A | I | `forecasting/tests/` |
| Frontend component tests (Vitest, planned) | R, A | I | I | I | `frontend/` |
| Performance checks (NFR-01, NFR-02) | I | R, A | R | I | `backend/`, `forecasting/` |
| User testing of key scenarios | R, A | I | I | C | `docs/ux/`, `docs/evidence-of-relevance/` |

### 3.5 Documentation, management and dissemination

| Work area | Birkhanym | Abzal | Evelina | Supervisor | Main artefacts |
|---|---|---|---|---|---|
| Project README | R, A | C | R | I | `README.md` |
| Contribution guide, repository structure, documentation index | C | C | R, A | I | `CONTRIBUTING.md`, `docs/README.md` |
| Technical documentation and API documentation | C | R, A | C | I | `backend/README.md`, `docs/architecture/api-contract.md` |
| Plan and milestones, responsibilities, task register | C | I | R, A | C | `docs/project-management/*` |
| Risk register and dependencies | R, A | C | C | C | `docs/project-management/risks.md` |
| Linear board upkeep | R | R | R, A | I | [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b) |
| Supervisor feedback log | R, A | I | I | C | `docs/supervision/feedback-log.md` |
| Thesis text | R | R | R | C | Chapters per section 5; accountable author per chapter |
| Scientific article | R | R | R, A | C | Article manuscript (April 2027); initial allocation, to be confirmed with the supervisor |
| Presentation and demo at pre-defenses | R, A | R | R | C | Presentation; demo run on the deployed prototype |

## 4. Repository ownership and default reviewers

| Path | Owner (A) | Default reviewer |
|---|---|---|
| `README.md`, `CONTRIBUTING.md`, `.gitignore`, `docs/README.md` | Evelina | Birkhanym |
| `backend/`, `docker-compose.yml`, `.env.example`, `.github/workflows/` | Abzal | Evelina |
| `forecasting/` | Evelina | Abzal |
| `frontend/`, `prototype/` | Birkhanym | Abzal |
| `docs/proposal.md`, `docs/requirements.md`, `docs/ux/`, `docs/evidence-of-relevance/`, `docs/existing-systems-comparison.md`, `docs/supervision/` | Birkhanym | Evelina |
| `docs/architecture/`, `docs/technology-comparison.md`, `docs/diagrams/` (architecture and database diagrams) | Abzal | Birkhanym |
| `docs/data/`, `docs/literature-review.md`, `docs/verification-and-evaluation-plan.md`, `docs/project-management/` | Evelina | Birkhanym |

The default reviewer is a starting point: any team member may review, but the owner of an area must approve changes to it that alter shared vocabulary (requirement IDs, entity names, API paths, the forecasting interface).

## 5. Thesis chapters (initial allocation)

| Chapter | Accountable author | Contributors |
|---|---|---|
| Introduction: problem, relevance, aim, objectives | Birkhanym | Evelina, Abzal |
| Literature review | Evelina | — |
| Analysis of existing systems and technologies | Birkhanym (systems), Abzal (technologies) | — |
| Requirements and user scenarios | Birkhanym | Abzal, Evelina |
| Architecture, database and API | Abzal | Evelina |
| Data preparation and forecasting models | Evelina | — |
| Shortage-risk calculation and notifications | Abzal | Evelina |
| Web interface and user testing | Birkhanym | — |
| Evaluation: experiments, error analysis, alert quality, integration testing | Evelina | Abzal, Birkhanym |
| Conclusion, limitations, future work | All | — |

The allocation follows the areas of responsibility and will be revised with the supervisor when the thesis structure is confirmed (April 2027).

## 6. Review rules and cross-area work

- Authors never approve their own pull requests; every pull request needs the approval of another team member (`CONTRIBUTING.md` section 5).
- Changes to `docs/architecture/api-contract.md` need the approval of Abzal and of at least one consumer of the API (Birkhanym for the frontend, Evelina for the forecasting payloads).
- Changes to the forecasting interface (`forecast_items`, `ForecastResult`) need the approval of Evelina and Abzal, and the API contract is updated in the same pull request.
- Changes to `docs/requirements.md` are proposed as a task, discussed at the weekly meeting and approved by Birkhanym; the verification plan and the use cases are updated together with the requirement.
- Work outside one's own area is welcome and is credited to its author; the owner of the area reviews it.

## 7. How individual contribution is tracked

| Evidence | Where | What it shows |
|---|---|---|
| Tasks | [Linear project PharmaStock](https://linear.app/pharmacy-kz/project/pharmastock-03a3f33ce30b); mirrored in [task-register.md](task-register.md) | Who was responsible for what, with deadlines, acceptance criteria and status |
| Commits and pull requests | GitHub repository `birxnm/diploma-pharmacy`, branches `PHA2-<n>-<slug>`, commits under the author's own name and e-mail | Who wrote which document, diagram or code and who reviewed it |
| Demos | Weekly supervisor meetings, recorded in `docs/supervision/feedback-log.md` | What was shown, when and by whom |
| Summary per member | Section 2 of `task-register.md`, updated before each pre-defense | Count of tasks per member and status |

The pre-defense packages list the contribution of each member by referring to these sources rather than to self-assessment.
