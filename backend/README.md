# backend

_PHA2-3 · Last updated: 2026-10-18_

FastAPI service of PharmaStock: REST API v1, PostgreSQL models and Alembic migrations, import and validation of consumption, stock and receipt data, forecast runs, shortage-risk calculation, users, roles and audit log. Owner: Abzal Bakhytov. The architecture is described in [docs/architecture/architecture.md](../docs/architecture/architecture.md); the endpoint list is kept in [docs/architecture/api-contract.md](../docs/architecture/api-contract.md).

## Status

As of 18 October 2026 the backend is a runnable scaffold: application factory, settings, CORS for the frontend development server, the health endpoint `GET /api/v1/health`, a PostgreSQL 16 service in Docker Compose and the SQLAlchemy engine/session wiring. Database models, Alembic migrations and the remaining endpoints of REST API v1 are planned.

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
│   └── db/
│       ├── session.py         # engine, session factory, get_db dependency
│       └── models.py          # SQLAlchemy models of the data entities (planned)
├── tests/
│   ├── test_health.py
│   └── test_session.py
├── pyproject.toml             # dependencies and pytest configuration
└── README.md
```

Routers live in `app/api/routes/`, one module per resource, and are mounted under the API prefix (`/api/v1`) in `create_app()`. Interactive API documentation is served at `/docs` (Swagger UI) and `/redoc`; the OpenAPI document at `/api/v1/openapi.json`. Endpoints that need the database take a session through the `get_db` dependency from `app/db/session.py`.

## Configuration

Settings are defined in `app/core/config.py` and read from environment variables or a `.env` file (the repository root `.env`, with an optional `backend/.env` taking priority). Every value has a placeholder default for local development; real values never go into Git. The root [.env.example](../.env.example) lists all variables; it is shared with Docker Compose.

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `PharmaStock` | Name reported by the health endpoint and the API documentation |
| `APP_ENVIRONMENT` | `development` | `development`, `test` or `production` |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `DATABASE_URL` | `postgresql+psycopg://pharmastock:change-me@localhost:5432/pharmastock` | SQLAlchemy connection URL (placeholder) |
| `SECRET_KEY` | `change-me` | Token signing key for authentication (FR-14), planned |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Origins allowed to call the API from a browser (Vite development server) |

## Setup

Prerequisites: Python 3.12; Docker with the Compose plugin for the database.

1. Create the environment file in the repository root and replace the placeholders:

   ```bash
   cp .env.example .env
   ```

2. Install the backend in a virtual environment:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Database with Docker Compose

PostgreSQL 16 runs as the `db` service of the root [docker-compose.yml](../docker-compose.yml). Its user, password, database name and published port come from `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`); Compose refuses to start when the first three are missing. Data is kept in the named volume `pgdata`.

```bash
docker compose up -d db          # start PostgreSQL in the background
docker compose ps                # the db service must report "healthy"
docker compose logs -f db        # follow the database log
docker compose down              # stop; add -v to delete the data volume as well
```

The backend connects with `DATABASE_URL` from `.env`, which by default points to `localhost:5432`, the port published by Compose. To open a `psql` shell inside the container:

```bash
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

A `backend` service is sketched in `docker-compose.yml` as a comment and will be enabled once the first endpoints beyond `/health` exist (NFR-07).

## Run

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open <http://localhost:8000/api/v1/health> or the interactive documentation at <http://localhost:8000/docs>. The health endpoint answers without touching the database, so it works whether or not the `db` service is running.

## Test

```bash
cd backend
python -m pytest -q
```

Tests use FastAPI's `TestClient` and build the application through `create_app(settings)` with an explicit `Settings` instance; the session tests point `DATABASE_URL` to an in-memory SQLite database. Neither needs PostgreSQL or a `.env` file. The same command runs in GitHub Actions on every pull request (NFR-08, workflow planned under `.github/workflows/ci.yml`).

## Planned next steps

- SQLAlchemy models for the data entities (`medicine_item`, `supplier`, `item_supplier`, `import_batch`, `consumption_record`, `stock_snapshot`, `receipt`, `planned_receipt`, ...) and Alembic migrations.
- Endpoints of REST API v1: authentication, items and history, imports, forecast runs, risks, notifications, thresholds, reports.
- `backend` service in Docker Compose and a deployment description (NFR-07).
