"""Application settings.

Settings are read from environment variables and from a ``.env`` file. The
repository root holds the single ``.env`` shared by Docker Compose and the
backend (copy ``.env.example`` and replace the placeholders); a ``backend/.env``
is also honoured and takes priority when both exist. Nothing here contains real
credentials: the defaults are placeholders for local development only.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import __version__

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Runtime configuration of the PharmaStock backend."""

    model_config = SettingsConfigDict(
        # Later files take priority over earlier ones.
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        validate_by_name=True,
        validate_by_alias=True,
    )

    app_name: str = Field(default="PharmaStock", validation_alias=AliasChoices("APP_NAME", "app_name"))
    app_version: str = __version__
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("APP_ENVIRONMENT", "environment"),
        description="development, test or production",
    )
    api_prefix: str = "/api/v1"
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level"))

    # Placeholder for local development; the real value comes from .env (DATABASE_URL).
    database_url: str = Field(
        default="postgresql+psycopg://pharmastock:change-me@localhost:5432/pharmastock",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    # Used for signing access tokens once authentication (FR-14) is implemented.
    secret_key: str = Field(default="change-me", validation_alias=AliasChoices("SECRET_KEY", "secret_key"))

    # Comma-separated list of origins allowed to call the API from a browser.
    # The default is the Vite development server of the frontend.
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance (read once, then cached)."""
    return Settings()
