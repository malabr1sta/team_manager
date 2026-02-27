import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.core.database import Base
from app.deps.base import get_settings
from app.identity import orm_models as identity_orm  # noqa: F401
from app.teams import orm_models as teams_orm  # noqa: F401
from app.tasks import orm_models as tasks_orm  # noqa: F401
from app.evaluations import orm_models as evaluations_orm  # noqa: F401
from app.scheduling import orm_models as scheduling_orm  # noqa: F401
from app.calendar import orm_models as calendar_orm  # noqa: F401


settings = get_settings()
VERSION_TABLE_SCHEMA = "public" if settings.use_schema else None


def build_database_url() -> str:
    """Build database URL for Alembic."""
    override_url = os.getenv("ALEMBIC_DATABASE_URL")
    if override_url:
        return override_url

    if all(
        [
            settings.database_user,
            settings.database_password,
            settings.database_host,
            settings.database_port,
            settings.database_name,
        ]
    ):
        return (
            f"postgresql+asyncpg://{settings.database_user}:"
            f"{settings.database_password}@"
            f"{settings.database_host}:{settings.database_port}/"
            f"{settings.database_name}"
        )
    return context.config.get_main_option("sqlalchemy.url")


DATABASE_URL = build_database_url()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=settings.use_schema,
        version_table_schema=VERSION_TABLE_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=settings.use_schema,
        version_table_schema=VERSION_TABLE_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
