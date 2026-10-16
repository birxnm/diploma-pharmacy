"""GET /api/v1/health - liveness information for monitoring and smoke tests."""

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app_name: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Service health")
def read_health(request: Request) -> HealthResponse:
    """Report that the service is up, together with its name, version and environment.

    The endpoint does not touch the database on purpose: it must answer even
    when PostgreSQL is unavailable, so that deployment checks can tell the two
    failures apart. A separate readiness check is planned.
    """
    settings: Settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
