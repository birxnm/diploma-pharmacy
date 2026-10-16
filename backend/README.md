# backend

_PHA2-3 · Last updated: 2026-10-16_

FastAPI service of PharmaStock: REST API v1, PostgreSQL models and Alembic migrations, import and validation of consumption, stock and receipt data, forecast runs, shortage-risk calculation, users, roles and audit log. Owner: Abzal Bakhytov. The architecture is described in [docs/architecture/architecture.md](../docs/architecture/architecture.md); the endpoint list is kept in [docs/architecture/api-contract.md](../docs/architecture/api-contract.md).

## Status

As of 16 October 2026 the backend is a runnable scaffold: application factory, settings, CORS for the frontend development server and the health endpoint `GET /api/v1/health`. Database models, Alembic migrations, Docker Compose and the remaining endpoints of REST API v1 are planned.

## Structure

```text
backend/
├── app/
│   ├── __init__.py            # package version
│   ├── main.py                # create_app() factory and the ASGI object `app`
│   ├── core/
│   │   └── config.py          # Settings (pydantic-settings), read from .env
│   ├── api/
│   │   └── routes/
│   │       └── health.py      # GET /api/v1/health
│   └── db/                    # SQLAlchemy models and session (planned)
├── tests/
│   └── test_health.py
├── pyproject.toml             # dependencies and pytest configuration
└── README.md
```

Routers live in `app/api/routes/`, one module per resource, and are mounted under the API prefix (`/api/v1`) in `create_app()`. Interactive API documentation is served at `/docs` (Swagger UI) and `/redoc`; the OpenAPI document at `/api/v1/openapi.json`.

## Configuration

Settings are defined in `app/core/config.py` and read from environment variables or a `.env` file (the repository root `.env`, with an optional `backend/.env` taking priority). Every value has a placeholder default for local development; real values never go into Git.

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `PharmaStock` | Name reported by the health endpoint and the API documentation |
| `APP_ENVIRONMENT` | `development` | `development`, `test` or `production` |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `DATABASE_URL` | `postgresql+psycopg://pharmastock:change-me@localhost:5432/pharmastock` | SQLAlchemy connection URL (placeholder) |
| `SECRET_KEY` | `change-me` | Token signing key for authentication (FR-14), planned |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Origins allowed to call the API from a browser (Vite development server) |

## Setup

Prerequisites: Python 3.12.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open <http://localhost:8000/api/v1/health> or the interactive documentation at <http://localhost:8000/docs>.

## Test

```bash
cd backend
python -m pytest -q
```

Tests use FastAPI's `TestClient` and build the application through `create_app(settings)` with an explicit `Settings` instance, so they do not depend on a database or on a `.env` file. The same command runs in GitHub Actions on every pull request (NFR-08, workflow planned under `.github/workflows/ci.yml`).

## Planned next steps

- Docker Compose with PostgreSQL 16 and a root `.env.example`.
- SQLAlchemy models for the data entities (`medicine_item`, `supplier`, `item_supplier`, `import_batch`, `consumption_record`, `stock_snapshot`, `receipt`, `planned_receipt`, ...) and Alembic migrations.
- Endpoints of REST API v1: authentication, items and history, imports, forecast runs, risks, notifications, thresholds, reports.
