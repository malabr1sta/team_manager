from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import calendar_type
from app.core.database import Base, IdMixin, TimestampMixin
from app.deps.base import get_settings


settings = get_settings()

SCHEMA = "calendar"
TABLE_ARGS = {"schema": SCHEMA} if settings.use_schema else {}
USER_FK = f"{SCHEMA}.calendar_user.id" if settings.use_schema else "calendar_user.id"


class CalendarUserOrm(Base, IdMixin, TimestampMixin):
    """Stores calendar user projection."""

    __tablename__ = "calendar_user"
    __table_args__ = TABLE_ARGS

    username: Mapped[str] = mapped_column(String, nullable=True)


class CalendarEventOrm(Base, IdMixin, TimestampMixin):
    """Stores calendar event projection."""

    __tablename__ = "calendar_event"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_type",
            "reference_id",
            name="uq_calendar_event_user_type_reference",
        ),
        *(() if not TABLE_ARGS else (TABLE_ARGS,)),
    )

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(USER_FK), nullable=False)
    event_type: Mapped[calendar_type.CalendarEventType] = mapped_column(
        Enum(calendar_type.CalendarEventType, name="calendar_event_type"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String, nullable=False, default="")
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reference_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
