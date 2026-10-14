# PharmaStock documentation

_PHA2-4 · Last updated: 2026-10-14_

This folder holds the project documentation of **PharmaStock**, the smart
supply chain analytics system for forecasting pharmaceutical inventory and
preventing medicine shortages in healthcare organizations (diploma project,
Astana IT University, School of Software Engineering, group SE-2414,
2026–2027). The index below lists every document the team maintains, in the
order in which it is read. Documents that have not been written yet are marked
**planned**; their names are fixed so that cross-references can be added now.

## Conventions

- All documents are Markdown, in English, concise, with tables for comparisons
  and requirement lists.
- Each document starts with its title followed by a line
  `_PHA2-<n> · Last updated: YYYY-MM-DD_` naming the task that produced it.
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
| `proposal.md` | Problem statement, aim, objectives, scope, expected outcomes, team and supervisor | Planned |
| `evidence-of-relevance/stakeholders.md` | Target users and stakeholders of a hospital pharmacy and what each needs from the system | Planned |
| `evidence-of-relevance/interview-guide.md` | Questions for interviews with pharmacy and procurement staff | Planned |
| `evidence-of-relevance/interview-log.md` | Record of interviews actually held (dates, roles, key findings) | Planned |

### Analysis

| Document | Purpose | Status |
|---|---|---|
| `literature-review.md` | Review of literature on intermittent demand forecasting and pharmaceutical inventory management | Planned |
| `existing-systems-comparison.md` | Comparison of existing inventory and forecasting systems and the gap this project addresses | Planned |
| `technology-comparison.md` | Justification of the technology stack (Python/FastAPI, PostgreSQL, forecasting libraries, Vue 3) | Planned |

### Requirements and design

| Document | Purpose | Status |
|---|---|---|
| `requirements.md` | Functional (`FR-01`...`FR-18`) and non-functional (`NFR-01`...`NFR-10`) requirements with MoSCoW priorities | Planned |
| `ux/user-scenarios.md` | User scenarios for the pharmacist, procurement specialist, department head and administrator | Planned |
| `ux/use-cases.md` | Use cases derived from the scenarios and mapped to requirements | Planned |
| `architecture/architecture.md` | System architecture: backend, forecasting module, database, web interface, deployment | Planned |
| `architecture/api-contract.md` | REST API v1 endpoints, request and response formats | Planned |
| `architecture/database-schema.md` | PostgreSQL schema: entities, attributes, relations | Planned |
| `data/data-specification.md` | Import file formats, data entities, validation rules, synthetic dataset description, stock-out flagging | Planned |
| `diagrams/` | Mermaid sources (`src/`) and exports (`export/`) of architecture, data-flow, database and sequence diagrams | See `diagrams/README.md` |

### Verification and management

| Document | Purpose | Status |
|---|---|---|
| `verification-and-evaluation-plan.md` | How the system is verified (tests, CI) and evaluated (baselines, MAE/WAPE, hold-out period, alert precision/recall, user testing) | Planned |
| `project-management/plan-and-milestones.md` | Monthly plan from October 2026 to the defense in June 2027, pre-defense milestones and Git tags | Planned |
| `project-management/risks.md` | Project risks (data access, integration, schedule) with mitigation | Planned |
| `project-management/responsibilities.md` | Detailed split of responsibilities between the three team members | Planned |
| `project-management/task-register.md` | Register of Linear issues (`PHA2-<n>`) with assignee, status and related pull requests | Planned |
| `supervision/feedback-log.md` | Log of supervisor meetings and feedback | Planned |

## Related documents outside `docs/`

| Document | Purpose |
|---|---|
| `../README.md` | Project overview and setup instructions |
| `../CONTRIBUTING.md` | Branching, commit messages, pull requests, review, tags |
| `../forecasting/README.md` | Scope and approach of the forecasting module |
| `../backend/README.md` | Backend service (placeholder until the first runnable version) |
| `../frontend/README.md` | Web interface (placeholder until the Vite scaffold is added) |
| `../prototype/README.md` | Static mockups of key screens |

## Adding a document

1. Create or pick the Linear issue and branch (`PHA2-<n>-<slug>`).
2. Put the file at the path listed above (or add a new row to this index).
3. Add the header line with the task ID and date.
4. Open a pull request; another team member reviews it before merge.
