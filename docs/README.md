# PharmaStock documentation

_PHA2-1 (updates PHA2-4) · Last updated: 2026-10-20_

This folder holds the project documentation of **PharmaStock**, the smart
supply chain analytics system for forecasting pharmaceutical inventory and
preventing medicine shortages in healthcare organizations (diploma project,
Astana IT University, School of Software Engineering, group SE-2414,
2026–2027). The index below lists every document the team maintains, in the
order in which it is read. Status is given as of 2026-10-20: **available**
means merged into `main`, **in review** means the pull request is open, and
**planned** means the document has not been written yet; names of planned
documents are fixed so that cross-references can be added now.

## Conventions

- All documents are Markdown, in English, concise, with tables for comparisons
  and requirement lists.
- Each document starts with its title followed by a header line that names the
  task that produced it and the date of the last update, for example
  `_PHA2-<n> · Last updated: YYYY-MM-DD_`; status, authors and reviewers may be
  added to the same line (`Task: PHA2-<n> · Last updated: YYYY-MM-DD · Status: ... · Author: ...`).
- Requirement IDs (`FR-01`...`FR-18`, `NFR-01`...`NFR-10`), data entity names,
  API paths and model names are shared vocabulary: use them verbatim, do not
  paraphrase.
- Diagrams are written in Mermaid. Sources live in `diagrams/src/*.mmd`,
  rendered copies in `diagrams/export/*.svg`; Markdown documents embed the
  Mermaid source so that GitHub renders it.
- Changes to documentation go through the same task, branch and pull request
  process as code (see `../CONTRIBUTING.md`).

## Index

### Project definition

| Document | Purpose | Status |
|---|---|---|
| `proposal.md` | Problem statement, aim, objectives, scope, expected outcomes, team and supervisor | Available (PHA2-5) |
| `evidence-of-relevance/stakeholders.md` | Target users and stakeholders of a hospital pharmacy and what each needs from the system | Available (PHA2-7) |
| `evidence-of-relevance/interview-guide.md` | Questions for interviews with pharmacy and procurement staff | Available (PHA2-7) |
| `evidence-of-relevance/interview-log.md` | Record of interviews actually held (dates, roles, key findings) | Available as a template (PHA2-7); interviews planned as PHA2-25 |

### Analysis

| Document | Purpose | Status |
|---|---|---|
| `literature-review.md` | Review of literature on intermittent demand forecasting and pharmaceutical inventory management | Available (PHA2-9) |
| `existing-systems-comparison.md` | Comparison of existing inventory and forecasting systems and the gap this project addresses | Available (PHA2-10) |
| `technology-comparison.md` | Justification of the technology stack (Python/FastAPI, PostgreSQL, forecasting libraries, Vue 3) | Available (PHA2-8) |

### Requirements and design

| Document | Purpose | Status |
|---|---|---|
| `requirements.md` | Functional (`FR-01`...`FR-18`) and non-functional (`NFR-01`...`NFR-10`) requirements with MoSCoW priorities and acceptance criteria | Available (PHA2-11) |
| `ux/user-scenarios.md` | User scenarios for the pharmacist, procurement specialist, department head and administrator | Available (PHA2-13) |
| `ux/use-cases.md` | Use cases derived from the scenarios and mapped to requirements, with the use case diagram | Available (PHA2-13) |
| `architecture/architecture.md` | System architecture: backend, forecasting module, database, web interface, deployment; system context and component diagrams | Available (PHA2-12) |
| `architecture/api-contract.md` | REST API v1 endpoints, request and response formats, internal interface of the forecasting package | Available (PHA2-17) |
| `architecture/database-schema.md` | PostgreSQL schema: entities, attributes, relations, constraints, indexes; ER diagram | Available (PHA2-14) |
| `data/data-specification.md` | Import file formats, data entities, validation rules, synthetic dataset description, stock-out flagging | Available (PHA2-15) |
| `diagrams/` | Mermaid sources (`src/`) and exports (`export/`): `system-context`, `component-diagram`, `use-case-diagram`, `er-diagram` | Available; see `diagrams/README.md` |

### Verification and management

| Document | Purpose | Status |
|---|---|---|
| `verification-and-evaluation-plan.md` | How the system is verified (tests, CI) and evaluated (baselines, MAE/WAPE, hold-out period, alert precision/recall, user testing) | Available (PHA2-19) |
| `project-management/plan-and-milestones.md` | Monthly plan from October 2026 to the defense in June 2027, pre-defense milestones and Git tags | Available (PHA2-20) |
| `project-management/risks.md` | Project risks (data access, integration, schedule) with owners, triggers and mitigation; dependencies between modules | Available (PHA2-20) |
| `project-management/responsibilities.md` | Detailed split of responsibilities between the three team members | Available (PHA2-20) |
| `project-management/task-register.md` | Register of Linear issues (`PHA2-<n>`) with responsible member, acceptance criteria, deadline, status and branch | Available (PHA2-20) |
| `project-management/ci.md` | What the CI workflow checks on every pull request and how to run the same checks locally | In review (PHA2-22) |
| `supervision/feedback-log.md` | Log of supervisor meetings and feedback | Available (PHA2-21) |

## Related documents outside `docs/`

| Document | Purpose | Status |
|---|---|---|
| `../README.md` | Project overview, development status, setup, run and test instructions | Available (PHA2-1) |
| `../CONTRIBUTING.md` | Tasks, branching, commit messages, pull requests, review, tags | Available (PHA2-4, updated with PHA2-1) |
| `../forecasting/README.md` | Scope, approach, package layout and backend interface of the forecasting module | Available (PHA2-6) |
| `../forecasting/data/README.md` | Synthetic development dataset: generator, committed sample, how to regenerate | Available (PHA2-15) |
| `../forecasting/experiments/README.md` | Experiment layout, configuration format, runner and result files, reproducibility rules | In review (PHA2-24) |
| `../backend/README.md` | Backend service: FastAPI scaffold, settings, database, tests | Available (PHA2-3) |
| `../frontend/README.md` | Web interface: Vue 3 + Vite scaffold, setup and scripts | In review (PHA2-23) |
| `../prototype/README.md` | Static mockups of key screens and their mapping to requirements | Available (PHA2-18) |

## Adding a document

1. Create or pick the Linear issue and branch (`PHA2-<n>-<slug>`).
2. Put the file at the path listed above (or add a new row to this index).
3. Add the header line with the task ID and date.
4. Open a pull request; another team member reviews it before merge.
