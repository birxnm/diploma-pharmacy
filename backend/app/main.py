"""FastAPI application factory and ASGI entry point.

Run locally with ``uvicorn app.main:app --reload`` from the ``backend/``
directory. Tests build their own instance with :func:`create_app` so that
settings can be overridden without touching the environment.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import Settings, get_settings


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application with its routers and middleware."""
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "REST API v1 of PharmaStock: import of consumption, stock and receipt "
            "data, medicine catalogue, forecast runs, shortage-risk assessment, "
            "notifications and reports."
        ),
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.api_prefix)

    return app


app = create_app()
