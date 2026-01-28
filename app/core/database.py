from sqlalchemy import DateTime, func, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    # Indicates whether to use a schema in the database.
    # This is needed for tests because SQLite does not support schemas.
    USE_SCHEMA: bool = True


class TimestampMixin:
    created_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_dttm: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IdMixin:

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

