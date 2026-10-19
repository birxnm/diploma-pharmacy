"""Tests for the engine/session wiring in app.db.session."""

from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db, get_engine, get_session_factory


def _reset_caches() -> None:
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()


@pytest.fixture
def sqlite_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # Environment variables take priority over .env, so this does not depend on
    # a developer's local configuration.
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    _reset_caches()
    yield
    get_engine().dispose()
    _reset_caches()


def test_engine_is_built_from_settings(sqlite_database: None) -> None:
    engine = get_engine()

    assert engine.url.drivername == "sqlite+pysqlite"
    assert get_engine() is engine  # cached, one engine per process


def test_get_db_yields_a_working_session_and_closes_it(sqlite_database: None) -> None:
    generator = get_db()
    session = next(generator)

    assert isinstance(session, Session)
    assert session.execute(text("SELECT 1")).scalar_one() == 1

    with pytest.raises(StopIteration):
        next(generator)  # runs the finally-block that closes the session
    assert not session.in_transaction()
