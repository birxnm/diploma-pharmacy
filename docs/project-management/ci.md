# PharmaStock — Continuous Integration

_PHA2-22 · Last updated: 2026-10-20 · Author: Abzal Bakhytov · Reviewer: Evelina Penkova_

This document describes what the continuous integration (CI) workflow of the
`diploma-pharmacy` repository checks, how those checks relate to the branch
policy in [CONTRIBUTING.md](../../CONTRIBUTING.md), and how to run the same
checks locally. The workflow itself is `.github/workflows/ci.yml`. It
implements requirement **NFR-08** ("Automated tests for backend and
forecasting run in CI on every pull request", Must) and is part of the
verification approach in
[verification-and-evaluation-plan.md](../verification-and-evaluation-plan.md).

## 1. When the workflow runs

| Event | Branches | Purpose |
|---|---|---|
| `pull_request` | any target branch (in practice `main`) | Check a task branch before review and merge |
| `push` | `main` only | Confirm that the merged baseline is still green |

A new push to the same branch cancels the run that is still in progress, so
only the latest commit of a pull request is checked. The workflow is named
`ci`; its jobs appear as `backend-tests`, `forecasting-tests` and `lint` in
the "Checks" tab of a pull request.

## 2. Jobs

All jobs run on `ubuntu-latest` with Python 3.12 (`actions/checkout@v4`,
`actions/setup-python@v5`). The two test jobs use the pip cache keyed on the
package's `pyproject.toml`.

| Job | Working directory | Steps | Blocks the merge |
|---|---|---|---|
| `backend-tests` | `backend/` | `pip install -e ".[dev]"`, then `pytest -q` | Yes |
| `forecasting-tests` | `forecasting/` | `pip install -e ".[dev]"`, then `pytest -q` | Yes |
| `lint` | repository root | `pip install ruff`, then `ruff check backend/ forecasting/` | No (advisory, see 2.3) |

### 2.1 `backend-tests`

Installs `backend/` as an editable package with its `dev` extra (`pytest`,
`httpx`) and runs the test suite in `backend/tests/`. The tests use the
FastAPI test client and an in-memory SQLite database that stands in for
PostgreSQL (the models use only portable column types), so no database
service is started in CI. `DATABASE_URL` is set inside the tests that need it;
no `.env` file is required or present on the runner. Pytest options
(`pythonpath`, `testpaths`) come from `backend/pyproject.toml`.

### 2.2 `forecasting-tests`

Installs `forecasting/` with its `dev` extra (`pytest`) and runs
`forecasting/tests/`: data validation (`forecasting.data`: schema, the
`is_stock_out` flag, regular weekly index), the baseline models
(`forecasting.models.baselines`), the metrics and the time-based split
(`forecasting.evaluation`) and the in-process interface
`forecasting.api.forecast_items`. Experiments under
`forecasting/experiments/` are not executed in CI; only unit tests are.

### 2.3 `lint`

Runs `ruff check` with the tool's default rule set over `backend/` and
`forecasting/`. The job is marked `continue-on-error: true`, so a lint
failure is shown in the run but does not fail the workflow and does not block
a merge. Reason: ruff is installed unpinned, and the default rule set of
current releases (0.17 at the time of writing) is broad; on the present
scaffold it reports a few dozen style findings (import order, `Decimal`
constructor style, quoted annotations and similar), while the classic
pyflakes/pycodestyle subset (`E4`, `E7`, `E9`, `F`) passes without findings.
No `[tool.ruff]` configuration has been added yet on purpose: the team first
agrees on a shared rule set and line length, writes it into
`backend/pyproject.toml` and `forecasting/pyproject.toml`, fixes the findings
(most are auto-fixable with `ruff check --fix`) and then removes
`continue-on-error` so that lint becomes a required check. This is a planned
follow-up task.

## 3. Branch policy and required checks

The branching model is defined in [CONTRIBUTING.md](../../CONTRIBUTING.md),
section 3 and section 5; CI is the automated part of it.

- `main` is the reviewed baseline. Nobody pushes to `main` directly; every
  change arrives through a pull request from a task branch `PHA2-<n>-<slug>`.
- A pull request is merged only when `backend-tests` and `forecasting-tests`
  are green, another team member has approved it, and the checklist in the
  pull request template is complete. The `lint` result is reviewed but does
  not block the merge until the follow-up in 2.3 is done.
- Submission states (`pre-defense-1`, `pre-defense-2`, `final-pre-defense`)
  are tagged on `main` only from a green run.

Branch protection for `main` is configured in the repository settings on
GitHub by the repository owner (Birkhanym Kazhymukhamet, @birxnm) once this
workflow is on `main`, because a check can be marked as required only after
it has run at least once:

| Setting | Value |
|---|---|
| Require a pull request before merging | On, 1 approving review |
| Require status checks to pass before merging | On: `backend-tests`, `forecasting-tests` |
| Require branches to be up to date before merging | On |
| Allow force pushes / deletions | Off |

Status: to be completed after the merge of PHA2-22; to be recorded in
[task-register.md](task-register.md) as follow-up tasks.

## 4. Running the same checks locally

Run the checks before pushing; CI runs exactly these commands.

```bash
# Backend
cd backend
pip install -e ".[dev]"
pytest -q

# Forecasting module
cd ../forecasting
pip install -e ".[dev]"
pytest -q

# Lint (advisory, from the repository root)
cd ..
pip install ruff
ruff check backend/ forecasting/
```

Both test suites run in a few seconds; most of the CI time is spent
installing dependencies, which the pip cache shortens on repeated runs.

## 5. Reading a failed run

| Symptom | Where to look |
|---|---|
| `backend-tests` or `forecasting-tests` red | Open the job, expand "Run ... tests"; `pytest -q` prints the failing test and assertion. Reproduce locally with the commands above. |
| Install step fails | A dependency added to `pyproject.toml` could not be resolved or built on Linux; check the package name and version bounds. |
| `lint` shows findings | Not blocking. Run `ruff check backend/ forecasting/` locally; fix what is relevant to the change or leave it for the lint follow-up task. |
| Run cancelled | A newer push to the same branch superseded it; look at the latest run. |

## 6. Not covered yet

| Area | Status |
|---|---|
| Frontend build and Vitest (`frontend/`) | Planned: a `frontend-build` job running `npm ci` and `npm run build` once the Vite scaffold (PHA2-23) is merged; component tests with Vitest later. |
| Tests against a real PostgreSQL service | Planned: a job with a `postgres:16` service for Alembic migrations and the import endpoint once those exist. |
| Lint as a required check | Planned, see 2.3. |
| Test coverage reporting | Not planned for pre-defense 1; may be added when the test suites grow. |

Section 5.4 of
[verification-and-evaluation-plan.md](../verification-and-evaluation-plan.md)
describes the target design (PostgreSQL service, coverage, frontend job); its job
names will be aligned to the actual `backend-tests` and `forecasting-tests` jobs.

## 7. Related documents

- [CONTRIBUTING.md](../../CONTRIBUTING.md) — branching model, commit format, pull requests and review
- [.github/PULL_REQUEST_TEMPLATE.md](../../.github/PULL_REQUEST_TEMPLATE.md) — checklist that references the CI result
- [verification-and-evaluation-plan.md](../verification-and-evaluation-plan.md) — test levels and evaluation methodology
- [task-register.md](task-register.md) — PHA2-22; follow-up tasks to be added
