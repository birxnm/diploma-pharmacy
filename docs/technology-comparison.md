# PharmaStock — Technology comparison

Task: PHA2-8 · Last updated: 2026-10-14 · Status: draft v0.1 (decisions 1–2 drafted; decisions 3–6 to be added) · Authors: Abzal Bakhytov (editor; decisions 1–3), Evelina Penkova (decision 4), Birkhanym Kazhymukhamet (decisions 5–6)

---

## 1. Purpose and method

This document records which technologies the team compared for PharmaStock, which it chose and why; it is the evidence for the architectural decisions ADR-1 to ADR-5 to be recorded in [architecture/architecture.md](architecture/architecture.md). Requirement IDs refer to [requirements.md](requirements.md), evaluation procedures to [verification-and-evaluation-plan.md](verification-and-evaluation-plan.md).

Criteria (C1 and C4 are decisive):

| ID | Criterion | Meaning for PharmaStock |
|---|---|---|
| C1 | Fit to requirements | Covers its share of FR-01…FR-18 without workarounds |
| C2 | Team experience | The team knows Python/FastAPI, PostgreSQL and Vue |
| C3 | Python ML ecosystem | Works with pandas, numpy and scikit-learn |
| C4 | Performance at our scale | ~1,000 items × 3 years weekly within 5 minutes on 4 vCPU / 8 GB (NFR-01); pages within 2 s with up to 5,000 items (NFR-02) |
| C5 | Maintenance and licensing | Actively released; permissive licence |
| C6 | Learning curve | Learnable by one member in days |
| C7 | Deployment simplicity | One Docker Compose file (NFR-07); GitHub Actions CI (NFR-08) |

Facts come from official sources only (package registries, official documentation, release pages, GitHub metadata); each facts cell links to them. Each decision ends with a box: Decision, Rationale, Consequences, Status.

## 2. Decision 1 — Server platform

Candidates: FastAPI, Django with Django REST Framework (DRF), Flask; the question is how much each gives for free to a JSON API in front of a Vue single-page application.

| Option | Facts and sources | Pros | Cons | Fit |
|---|---|---|---|---|
| FastAPI | Current 0.1xx line, still 0.x versioning (release notes); MIT. OpenAPI/JSON Schema, Swagger UI and ReDoc by default, Pydantic validation, Starlette performance; very active, with frequent minor releases. [PyPI](https://pypi.org/pypi/fastapi/json), [release](https://api.github.com/repos/fastapi/fastapi/releases/latest), [releases](https://github.com/fastapi/fastapi/releases), [repo](https://github.com/fastapi/fastapi), [features](https://fastapi.tiangolo.com/features/), [tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) | OpenAPI contract for the frontend at no cost; Pydantic schemas double as DTOs; async; least boilerplate | 0.x, so minor releases can change behaviour; no built-in ORM or admin | High |
| Django + DRF | Django 6.1.2 (6.1: 2026-08-05; 5.2 LTS to April 2028); BSD-3-Clause; Python ≥ 3.12. DRF 3.18.3 (2026-10-06); BSD-3-Clause. Built-in admin, authentication and CSRF/XSS protection; DRF adds browsable API, serializers, authentication. [PyPI](https://pypi.org/pypi/Django/json), [downloads](https://www.djangoproject.com/download/), [6.1 notes](https://docs.djangoproject.com/en/stable/releases/6.1/), [repo](https://github.com/django/django), [overview](https://www.djangoproject.com/start/overview/), [DRF PyPI](https://pypi.org/pypi/djangorestframework/json), [DRF notes](https://www.django-rest-framework.org/community/release-notes/), [DRF home](https://www.django-rest-framework.org/), [DRF repo](https://github.com/encode/django-rest-framework) | Mature ORM, migrations and admin; LTS line; largest ecosystem; strong security defaults | Two frameworks to learn; synchronous-first; heavier than needed; OpenAPI needs drf-spectacular | Medium |
| Flask | 3.1.3 (2026-02-19); BSD-3-Clause. Lightweight WSGI framework; validation, SQLAlchemy and Celery via extensions. [PyPI](https://pypi.org/pypi/Flask/json), [docs](https://flask.palletsprojects.com/en/stable/), [repo](https://github.com/pallets/flask) | Smallest learning curve; stable 3.x line; huge extension ecosystem | No built-in validation, serialisation or OpenAPI; async only via Quart or gevent | Low–medium |

> **Decision.** FastAPI on uvicorn serving the REST/JSON API of ADR-3, Pydantic models for every request and response, SQLAlchemy 2.x with Alembic (ADR-2).
> **Rationale.** C1: the backend is a JSON API for the Vue views (FR-05, FR-07, FR-09) and hosts the forecasting package (FR-06, ADR-1); the generated OpenAPI schema becomes the contract in `architecture/api-contract.md` (PHA2-17; NFR-08). C2: the team already uses FastAPI; Django would win only if a server-rendered admin were needed (covering FR-03, FR-04, FR-10), but the UI is a separate Vue application. C4, C7: Starlette performance (NFR-02); one framework, one process, one image.
> **Consequences.** Pin exact `fastapi` and `pydantic` versions and read release notes before upgrading; import validation (FR-02) uses Pydantic schemas; the forecasting package keeps its own input checks (NFR-06).
> **Status.** Accepted.

## 3. Decision 2 — Data storage

Candidates: PostgreSQL, MySQL, MongoDB, with TimescaleDB as an optional PostgreSQL extension. The workload mixes relational entities with one weekly series per item.

| Option | Facts and sources | Pros | Cons | Fit |
|---|---|---|---|---|
| PostgreSQL | 18.6 current (minors 18.6/17.11/16.15/15.19/14.24: 2026-08-13); PostgreSQL License (BSD/MIT-like); five years of support per major, 16 to 2028-11-09. [versioning](https://www.postgresql.org/support/versioning/), [home](https://www.postgresql.org/), [licence](https://www.postgresql.org/about/licence/) | Relational model matches inventory entities; window functions for weekly aggregation and lags; team experience; permissive licence | No specialised time-series storage without an extension; schema designed up front | High |
| TimescaleDB (extension) | 2.30.2 (2026-09-29); PostgreSQL 16/17/18. Hypertables partition by time but behave like regular tables; the Apache-2.0 edition lacks continuous aggregates and retention; the Community edition (TSL) is free to self-host but not to offer as a service. [releases](https://github.com/timescale/timescaledb/releases), [repo](https://github.com/timescale/timescaledb), [editions](https://www.tigerdata.com/docs/about/latest/timescaledb-editions), [hypertables](https://www.tigerdata.com/docs/use-timescale/latest/hypertables) | Zero migration cost; automatic partitioning and continuous aggregates if history grows | Extra dependency; advanced features TSL-only; not needed at our volume | Optional |
| MySQL Community | 8.4.12 LTS, 9.7.3 (9.7 labelled LTS on the downloads page) and 26.7.1 Innovation, all 2026-08-18; 8.0 still offered; GPL. LTS series alongside a calendar-versioned Innovation track. [community](https://www.mysql.com/products/community/), [downloads](https://dev.mysql.com/downloads/mysql/), [8.4 notes](https://dev.mysql.com/doc/relnotes/mysql/8.4/en/), [9.7 notes](https://dev.mysql.com/doc/relnotes/mysql/9.7/en/), [Innovation notes](https://dev.mysql.com/doc/relnotes/mysql/26.10/en/) | Widely known; LTS line; GPL acceptable academically | No team experience; release model in flux; weaker analytics ecosystem; no TimescaleDB equivalent | Low |
| MongoDB Community | 9.0 (9.0.0: 2026-09-28; 9.0.4: 2026-10-13); SSPL v1, whose Section 13 applies only when MongoDB itself is offered as a service. Time-series collections since 5.0 restrict updates. [release notes](https://www.mongodb.com/docs/manual/release-notes/), [9.0 notes](https://www.mongodb.com/docs/manual/release-notes/9.0/), [SSPL FAQ](https://www.mongodb.com/legal/licensing/server-side-public-license/faq), [SSPL text](https://www.mongodb.com/legal/licensing/server-side-public-license), [time-series](https://www.mongodb.com/docs/manual/core/timeseries-collections/) | Flexible schema; native time-series collections; actively patched | Inventory data is relational and needs joins and transactions; SSPL is not OSI-approved; no team experience | Low |

> **Decision.** PostgreSQL as the single store through SQLAlchemy 2.x and Alembic (ADR-2). `docker-compose.yml` will pin `postgres:16` (PHA2-3), supported until 2028-11-09, beyond the project end; 17 or 18 are equally acceptable (a tag change plus a run of the migrations and tests against the new image). TimescaleDB is an upgrade path only.
> **Rationale.** C1: items, suppliers, stock, receipts, forecast runs and the audit log (FR-03, FR-04, FR-08, FR-10, FR-15) need joins and transactions; MongoDB would suit event ingestion, not a catalogue with stock movements. C4: 1,000 items × 156 weeks is about 156,000 rows for a forecast run (NFR-01) and 5,000 items about 780,000 rows for page queries (NFR-02); an index on `(item_id, period_start)` serves both without partitioning. C2, C5: team experience; permissive licence; five-year support.
> **Consequences.** The schema (`architecture/database-schema.md`) and the weekly `period_start` convention (ADR-4) are designed up front; the consumption table can become a hypertable later without a rewrite.
> **Status.** Accepted.

## 4. Decisions 3–6 — to be added

| # | Decision | Candidates | Author | Status |
|---|---|---|---|---|
| 3 | Component interaction | REST/JSON vs gRPC vs message queue; in-process package vs separate forecasting service | Abzal Bakhytov | To be added |
| 4 | Forecasting toolkit | statsforecast + statsmodels vs Prophet vs LightGBM + scikit-learn (sktime, darts noted) | Evelina Penkova | To be added |
| 5 | Frontend framework | Vue 3 vs React vs Angular | Birkhanym Kazhymukhamet | To be added |
| 6 | Charting library | Chart.js vs Apache ECharts vs D3 | Birkhanym Kazhymukhamet | To be added |
