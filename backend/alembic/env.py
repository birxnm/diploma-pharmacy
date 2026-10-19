"""Alembic environment: wires the migration context to the application models.

The database URL comes from the application settings (``DATABASE_URL`` in
``.env``), so that no credentials are stored in ``alembic.ini``.
``target_metadata`` is the metadata of ``app.db.base.Base``; importing
``app.db.models`` registers every table on it, which is what
``alembic revision --autogenerate`` compares with the live database.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db import models  # noqa: F401  (registers the tables on Base.metadata)
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# configparser interpolation: a literal "%" in the URL has to be doubled.
config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit the migration SQL to stdout without connecting (``alembic upgrade head --sql``)."""
    url = config.get_main_option("sqlalchemy.url") or ""
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=url.startswith("sqlite"),
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations through a real connection built from ``sqlalchemy.url``."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            # SQLite cannot ALTER most things in place; batch mode recreates the table.
            render_as_batch=connection.dialect.name == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
