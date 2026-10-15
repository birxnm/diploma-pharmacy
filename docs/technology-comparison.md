# PharmaStock — Technology comparison

Task: PHA2-8 · Last updated: 2026-10-15 · Status: draft v0.2 (decisions 1–3 and summary drafted; decisions 4–6 to be added) · Authors: Abzal Bakhytov (editor; decisions 1–3), Evelina Penkova (decision 4), Birkhanym Kazhymukhamet (decisions 5–6)

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

## 4. Decision 3 — Component interaction

Two questions: which protocol connects the components (REST/JSON, gRPC or a message queue) and whether forecasting is an in-process package or a separate service.

| Option | Facts and sources | Pros | Cons | Fit |
|---|---|---|---|---|
| REST/JSON with OpenAPI; in-process forecasting package | Open standards; OpenAPI generated by FastAPI; no extra infrastructure. `BackgroundTasks` run in-process; Celery is advised only for heavy work across processes or servers. [features](https://fastapi.tiangolo.com/features/), [tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) | Browser consumes JSON natively; Swagger UI as shared test console; one repository, one image, one deployment | Long runs must not block requests; ML dependencies live in the backend image | High |
| gRPC to a separate forecasting service | grpcio 1.84.0 (2026-09-11); Apache-2.0. HTTP/2 RPC with `.proto` definitions compiled into stubs. [PyPI](https://pypi.org/pypi/grpcio/json), [release](https://api.github.com/repos/grpc/grpc/releases/latest), [quickstart](https://grpc.io/docs/languages/python/quickstart/) | Typed protobuf contracts; efficient binary transport | Protobuf toolchain and generated code; browsers still need HTTP/JSON or a gRPC-Web proxy | Low |
| Celery with RabbitMQ or Redis | Celery 5.6.3 (2026-03-26); BSD-3-Clause; needs a broker; no Windows support. RabbitMQ 4.3.6 (2026-09-16); MPL-2.0. Redis 8.10.2 (2026-09-17); RSALv2 / SSPLv1 / AGPLv3 since 8.0. [Celery PyPI](https://pypi.org/pypi/celery/json), [Celery intro](https://docs.celeryq.dev/en/stable/getting-started/introduction.html), [RabbitMQ releases](https://www.rabbitmq.com/release-information), [RabbitMQ repo](https://github.com/rabbitmq/rabbitmq-server), [Redis licences](https://redis.io/legal/licenses/), [Redis release](https://api.github.com/repos/redis/redis/releases/latest) | Decouples long computations; retries, scheduling, worker scaling | Broker and workers to run and document; no Windows support on student laptops; Redis 8 licensing non-standard | Medium–low |

> **Decision.** REST/JSON with OpenAPI between the Vue frontend and FastAPI (ADR-3); forecasting as the in-process package `forecasting/` with one stable entry-point function called by the backend (ADR-1); runs as background jobs inside the backend that write forecasts and risk flags to PostgreSQL (ADR-5). gRPC rejected; Celery deferred.
> **Rationale.** C1, C7: three people, one deployable (NFR-07); the contract is visible in Swagger UI and testable in CI (NFR-08). C4: a run (FR-06) is a batch job whose stored results are read later (FR-07, FR-09), so NFR-02 is unaffected. gRPC would pay off only for a shared service; Celery when runs outgrow one process.
> **Consequences.** ADR-5 is confirmed by a timed run on the synthetic dataset (NFR-01); if the limit is missed inside the API process, Celery with RabbitMQ (MPL-2.0, avoiding the RSALv2/SSPLv1/AGPLv3 terms of Redis 8) is the next step. The package stays importable without the backend so that experiments (NFR-05) run standalone.
> **Status.** Accepted; the background-run mechanism (ADR-5) stays provisional until the NFR-01 timing.

## 5. Summary of decisions

| # | Decision | Chosen option | Alternatives considered | Status |
|---|---|---|---|---|
| 1 | Server platform | FastAPI, Pydantic, SQLAlchemy 2.x, Alembic | Django + DRF; Flask | Accepted |
| 2 | Data storage | PostgreSQL (`postgres:16` pinned; 17/18 acceptable) | MySQL; MongoDB; TimescaleDB as optional extension | Accepted |
| 3 | Component interaction | REST/JSON (OpenAPI); in-process forecasting package; background runs | gRPC to a separate service; Celery with RabbitMQ/Redis (deferred) | Accepted |
| 4 | Forecasting toolkit | To be added (Evelina Penkova) | statsforecast + statsmodels; Prophet; LightGBM + scikit-learn; sktime, darts | To be added |
| 5 | Frontend framework | To be added (Birkhanym Kazhymukhamet) | Vue 3; React; Angular | To be added |
| 6 | Charting library | To be added (Birkhanym Kazhymukhamet) | Chart.js; Apache ECharts; D3 | To be added |
