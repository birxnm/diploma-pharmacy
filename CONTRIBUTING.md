# Contributing to PharmaStock

_PHA2-4 · Last updated: 2026-10-14_

This guide describes how the team works in the `diploma-pharmacy` repository:
how tasks are tracked, how branches and commits are named, how changes are
reviewed and what must never be committed. It applies to code, documentation
and diagrams alike. Individual contribution is tracked by tasks, commits and
demos, so every meaningful piece of work must be visible in Linear and in the
Git history under the author's own name.

## 1. Team and areas of responsibility

| Member | GitHub | Area |
|---|---|---|
| Birkhanym Kazhymukhamet | @birxnm | Requirements and user scenarios, UX mockups, web interface (`frontend/`, `prototype/`), visualisation of forecasts and alerts, user testing |
| Abzal Bakhytov | — | Backend (`backend/`): Python, database, REST API, import and validation, risk calculation, access control and audit log, deployment, API documentation |
| Evelina Penkova | @etoevelina | Data preparation and analysis, forecasting models and experiments (`forecasting/`), evaluation on a hold-out period, serving forecasts through the API together with Abzal |

The detailed split of tasks is kept in `docs/project-management/responsibilities.md`
(planned). Changes outside your own area are welcome, but the owner of that
area reviews them.

## 2. Task tracking

- Tasks live in the Linear team **PHA2** (link will be added when the
  instance is confirmed). Task IDs look like `PHA2-2`, `PHA2-4`, ...
- Create **one Linear issue per meaningful work item**: a document, a feature,
  a bug fix, an experiment, a set of diagrams. Trivial follow-ups (typo, broken
  link) may be committed under the task they belong to.
- Every task has an assignee, an estimate in hours and a link to the pull
  request once it exists. Weekly supervisor meetings review the task board.
- The task ID is the thread that connects the task, the branch, the commits
  and the pull request. Always include it.

## 3. Branching model

- `main` is the **reviewed baseline**. It must always be in a consistent,
  presentable state: documentation renders, tests pass, the project can be set
  up from the README. Nobody pushes to `main` directly; every change arrives
  through a pull request.
- Work happens on **task branches** cut from the latest `main`. Branch names
  follow the pattern `PHA2-<n>-<slug>`, where `<slug>` is a short, lower-case,
  hyphen-separated description in English:

  ```text
  PHA2-4-repository-structure
  PHA2-11-functional-requirements
  PHA2-23-croston-baseline
  ```

- Start a task from an up-to-date `main`:

  ```bash
  git checkout main
  git pull origin main
  git checkout -b PHA2-11-functional-requirements
  ```

- Keep branches short-lived (days, not weeks). If `main` moves on while you
  work, bring the changes in with `git merge main` or `git rebase main` before
  opening the pull request.
- Branches are deleted after the pull request is merged.

## 4. Commit messages

Commit messages are written in **English** and follow the format

```text
type(scope): subject [PHA2-<n>]
```

- `type` is one of:

  | Type | Use for |
  |---|---|
  | `feat` | New functionality (backend, forecasting, frontend) |
  | `fix` | Bug fixes |
  | `ref` | Refactoring without a change in behaviour |
  | `docs` | Documentation, diagrams, README files, thesis-related texts |
  | `test` | Adding or changing tests only |
  | `chore` | Repository housekeeping: dependencies, configuration, tooling |
  | `ci` | GitHub Actions workflows and CI configuration |

- `scope` names the part of the repository or the topic that changed, for
  example `backend`, `forecasting`, `frontend`, `prototype`, `docs`,
  `requirements`, `architecture`, `db`, `api`, `data`, `repo`, `readme`.
- `subject` is a short imperative sentence ("add", "fix", "update", not
  "added" or "adds"), without a trailing period, and the whole first line
  stays within 72 characters.
- The Linear issue ID goes in **square brackets at the end of the subject**.
- A body is optional; use it to explain *why* a change was made when the
  subject is not enough. Separate it from the subject with a blank line.

Examples:

```text
docs(requirements): add functional requirements [PHA2-11]
feat(forecasting): add Croston and SBA baselines [PHA2-23]
fix(backend): reject negative quantities on import [PHA2-30]
test(forecasting): cover WAPE with zero actuals [PHA2-23]
chore(repo): add .gitignore and contribution guide [PHA2-4]
ci(github): run backend and forecasting tests on pull requests [PHA2-5]
```

Commit small, coherent changes. One commit should be understandable on its own
and should not mix unrelated work (for example a document and a code change).

## 5. Pull requests and review

- Open **one pull request per task**, from the task branch into `main`, and
  fill in the template in `.github/PULL_REQUEST_TEMPLATE.md` (task, summary of
  changes, how it was checked, checklist).
- The pull request title follows the same format as commit messages, for
  example `docs(requirements): add functional requirements [PHA2-11]`.
- A pull request is merged only when:
  1. CI is green (automated tests for the backend and the forecasting module
     run on every pull request, see `.github/workflows/ci.yml`, planned);
  2. it has been **reviewed and approved by another team member** — authors do
     not approve their own work; the owner of the affected area is the
     preferred reviewer;
  3. the checklist in the description is complete.
- Reviewers check that the change matches the task, that documentation and
  tests were updated, that naming agrees with the shared vocabulary in
  `docs/` (entity names, requirement IDs, API paths) and that nothing in the
  "never commit" list below slipped in.
- Merge with a merge commit (the GitHub default) so that the task's commits
  and their authors stay visible in the history. Delete the branch afterwards.

## 6. Code, tests and documentation conventions

- **Python** (`backend/`, `forecasting/`): Python 3.12, type hints on public
  functions, tests with `pytest` next to the package in `tests/`. Run the
  package's test suite locally before pushing. Formatting and linting settings
  live in each package's `pyproject.toml`.
- **Frontend** (`frontend/`): Vue 3 + Vite + TypeScript. `npm run build` must
  succeed; component tests with Vitest are planned.
- **Documentation** (`docs/`): Markdown, English, concise, tables for
  comparisons and requirement lists. Each document starts with its title and a
  line `_PHA2-<n> · Last updated: YYYY-MM-DD_`. Requirement IDs (`FR-xx`,
  `NFR-xx`), entity names and API paths are reused verbatim across documents,
  code and diagrams.
- **Diagrams**: Mermaid sources in `docs/diagrams/src/*.mmd`, rendered copies in
  `docs/diagrams/export/*.svg`. Edit the source first, then re-export.
- **Experiments** (`forecasting/experiments/`): every run has a versioned
  configuration file and a fixed random seed; results are saved per run so that
  the comparison can be reproduced from a clean checkout.

## 7. What must never be committed

- **Secrets**: passwords, tokens, API keys, private keys, database URLs with
  credentials. Configuration is read from environment variables; `.env` is
  ignored by Git and the tracked `.env.example` contains only placeholders
  such as `POSTGRES_PASSWORD=change-me`.
- **Datasets**: raw or processed consumption, stock and receipt data, whether
  real or synthetic in full size. Only the small, documented samples under
  `forecasting/data/sample/` are tracked. Data obtained from a partner
  organization is subject to its conditions of use and stays outside Git.
- **Personal data of any kind.** The system processes no patient data, and the
  repository must not contain it either.
- Local environments, build output, caches, IDE settings and databases (see
  `.gitignore`).

If something sensitive was committed by mistake, do not just delete it in a
new commit: tell the team immediately, rotate the secret, and rewrite the
history of the branch before it reaches `main`.

## 8. Tags and submissions

Submission states of the repository are marked with annotated Git tags on
`main`:

| Tag | Milestone |
|---|---|
| `pre-defense-1` | First pre-defense materials (October 2026) |
| `pre-defense-2` | Second pre-defense materials |
| `final-pre-defense` | Final pre-defense before the thesis defense (2027) |

A tag is created from `main` once the submission package has been checked by
the team, and it is never moved afterwards.

## 9. Repository layout

```text
.
├── README.md                 # project overview and setup (root)
├── CONTRIBUTING.md           # this guide
├── .gitignore
├── .env.example              # configuration placeholders, no real values
├── docker-compose.yml        # PostgreSQL and services for local development
├── .github/                  # pull request template, GitHub Actions workflows
├── backend/                  # FastAPI service, database models, REST API
├── forecasting/              # forecasting package, synthetic data, experiments
├── frontend/                 # Vue 3 + Vite web interface
├── prototype/                # static HTML/CSS mockups of key screens
└── docs/                     # proposal, requirements, architecture, plans, diagrams
```

Directories that are not yet populated contain a short README describing what
will live there. The documentation index is `docs/README.md`.
