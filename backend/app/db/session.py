"""Database engine, session factory and the ``get_db`` request dependency.

The engine is created lazily from ``settings.database_url``, so importing the
application (in tests, in Alembic, in tooling) does not require a reachable
database. ``pool_pre_ping`` makes the pool drop connections that PostgreSQL
closed while the service was idle.
"""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Process-wide SQLAlchemy engine bound to ``DATABASE_URL``."""
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Session factory bound to the process-wide engine."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one SQLAlchemy session per request.

    Usage: ``def endpoint(db: Session = Depends(get_db))``. The session is
    closed when the request finishes; commits are explicit in the service
    code, so a failed request never leaves a half-written transaction behind.
    """
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
