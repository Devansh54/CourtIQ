"""Alembic Environment Configuration for CourtIQ.

Connects securely using MIGRATION_DATABASE_URL or DATABASE_URL from
courtiq.core.config, supporting both offline SQL generation and online migrations.
"""

import sys
from logging.config import fileConfig
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from courtiq.core.config import get_settings

config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database URL dynamically from CourtIQ centralized settings
settings = get_settings()
custom_url = config.attributes.get("target_url")
if custom_url:
    config.set_main_option("sqlalchemy.url", custom_url)
else:
    if not settings.migration_database_url:
        from courtiq.core.exceptions import ConfigurationError
        raise ConfigurationError(
            "MIGRATION_DATABASE_URL is not configured. "
            "Alembic migrations require dedicated MIGRATION_DATABASE_URL with courtiq_migrator credentials."
        )
    config.set_main_option("sqlalchemy.url", settings.migration_database_url)

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        url = config.get_main_option("sqlalchemy.url")
        from sqlalchemy import create_engine
        connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

