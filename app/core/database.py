from sqlalchemy import DateTime, func, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
)


class Base(AsyncAttrs, DeclarativeBase):
    # Indicates whether to use a schema in the database.
    # This is needed for tests because SQLite does not support schemas.
    USE_SCHEMA: bool = True

    @declared_attr
    def created_dttm(cls) -> Mapped[DateTime]:
        return mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_dttm(cls) -> Mapped[DateTime]:
        return mapped_column(
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

