# backend

_PHA2-3 · Last updated: 2026-10-19_

FastAPI service of PharmaStock: REST API v1, PostgreSQL models and Alembic migrations, import and validation of consumption, stock and receipt data, forecast runs, shortage-risk calculation, users, roles and audit log. Owner: Abzal Bakhytov. The architecture is described in [docs/architecture/architecture.md](../docs/architecture/architecture.md); the endpoint list is kept in [docs/architecture/api-contract.md](../docs/architecture/api-contract.md) and the tables in [docs/architecture/database-schema.md](../docs/architecture/database-schema.md).

## Status

As of 19 October 2026 the backend is a runnable scaffold: application factory, settings, CORS for the frontend development server, the health endpoint `GET /api/v1/health`, a PostgreSQL 16 service in Docker Compose, the SQLAlchemy engine/session wiring, the models of the catalogue and imported time series, and the Alembic setup (no migration files yet). The remaining entities and the endpoints of REST API v1 are planned.

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
│       ├── base.py            # declarative Base with the constraint naming convention
│       ├── models.py          # SQLAlchemy models of the data entities
│       └── session.py         # engine, session factory, get_db dependency
├── alembic/
│   ├── env.py                 # migration environment bound to Base.metadata and DATABASE_URL
│   ├── script.py.mako         # template for new migration files
│   └── versions/              # migration files (none yet)
├── alembic.ini
├── tests/
│   ├── test_health.py
│   ├── test_session.py
│   └── test_models.py
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

## Database models

`app/db/models.py` maps the data entities of the project documentation with SQLAlchemy 2.x declarative models. Table and column names are reused verbatim from `docs/architecture/database-schema.md`, the API schemas and the import file formats.

| Table | Columns | Notes |
|---|---|---|
| `medicine_item` | id, code, name, unit, group, is_active | Catalogue (FR-03); `code` is unique and is the key used in import files |
| `supplier` | id, name | FR-04 |
| `item_supplier` | item_id, supplier_id, lead_time_days, is_primary | Composite primary key; lead time in days drives the risk level (FR-08) |
| `import_batch` | id, file_name, source_type, imported_at, user_id, status, summary_json | One uploaded file (FR-01); status `pending`, `processing`, `completed`, `failed`; `summary_json` keeps validation errors and the data-quality summary (FR-02, FR-18); the foreign key to `app_user` follows with FR-14 |
| `consumption_record` | id, item_id, period_start, quantity, import_batch_id | One row per item and week (unique); every row belongs to an import batch |
| `stock_snapshot` | id, item_id, period_start, quantity_on_hand, is_stock_out, import_batch_id | One row per item and week (unique); `quantity_on_hand` is the closing balance of the week; `is_stock_out` marks censored demand (FR-17) |
| `receipt` | id, item_id, received_on, quantity, supplier_id, import_batch_id | Received deliveries; one row per item, date and supplier; `quantity > 0` |
| `planned_receipt` | id, item_id, expected_on, quantity, supplier_id, status | Expected deliveries (FR-10); status `planned`, `received`, `cancelled`; `quantity > 0` |

Conventions follow `docs/architecture/database-schema.md`: `period_start` is the Monday of the ISO week; quantities are `NUMERIC(14, 3)`, non-negative for consumption and stock and positive for deliveries (check constraints); enumerations (`source_type` and `status` of `import_batch`, `status` of `planned_receipt`) are Python `StrEnum` classes stored as `varchar` with a CHECK constraint, not as PostgreSQL `ENUM` types; JSON payloads are `jsonb` on PostgreSQL; the time-series tables use `bigint` identity keys; foreign keys to `medicine_item` and `import_batch` are `ON DELETE RESTRICT`. PostgreSQL-only types are declared as dialect variants so that the tests can run on SQLite. Index and constraint names follow the naming convention in `app/db/base.py` and the names of the schema document, so that migrations can refer to them. The remaining entities (`forecast_run`, `forecast`, `risk_assessment`, `notification`, `app_user`, `audit_log`, `threshold_config`) are added with their own tasks.

## Migrations with Alembic

Alembic is configured in `alembic.ini` and `alembic/env.py`. The environment imports `app.db.models` and uses `Base.metadata` as the target, and it takes the database URL from the application settings (`DATABASE_URL`), so `alembic.ini` contains no credentials. There are no migration files yet; the first one will be generated when the schema is agreed on in `docs/architecture/database-schema.md`.

```bash
cd backend
alembic revision --autogenerate -m "create catalogue and import tables"   # writes alembic/versions/<date>_<rev>_<slug>.py
alembic upgrade head                                                      # apply to the database from DATABASE_URL
alembic upgrade head --sql                                                # print the SQL instead of applying it
alembic downgrade -1                                                      # revert the last migration
```

Review every autogenerated file before committing it: Alembic detects tables, columns, indexes and constraints, but not every change (for example renamed columns appear as drop and add).

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

Tests use FastAPI's `TestClient` and build the application through `create_app(settings)` with an explicit `Settings` instance; the session and model tests run against an in-memory SQLite database, on which the schema is created from the models. Neither needs PostgreSQL or a `.env` file. The same command runs in GitHub Actions on every pull request (NFR-08, workflow planned under `.github/workflows/ci.yml`).

## Planned next steps

- First Alembic migration once the schema is reviewed; models for `forecast_run`, `forecast`, `risk_assessment`, `notification`, `app_user`, `audit_log` and `threshold_config`.
- Endpoints of REST API v1: authentication, items and history, imports, forecast runs, risks, notifications, thresholds, reports.
- `backend` service in Docker Compose and a deployment description (NFR-07).
