"""Tests for GET /api/v1/health and the application factory."""

import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    # _env_file=None isolates the tests from any .env on the developer machine.
    return Settings(_env_file=None, environment="test")


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_reports_app_metadata(client: TestClient, settings: Settings) -> None:
    body = client.get("/api/v1/health").json()

    assert body == {
        "status": "ok",
        "app_name": settings.app_name,
        "version": __version__,
        "environment": "test",
    }


def test_health_is_mounted_under_api_prefix_only(client: TestClient) -> None:
    assert client.get("/health").status_code == 404


def test_cors_preflight_allows_vite_dev_server(client: TestClient) -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client: TestClient) -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers


def test_openapi_document_is_served_under_api_prefix(client: TestClient, settings: Settings) -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == settings.app_name
