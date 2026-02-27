from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, IdMixin, TimestampMixin
from app.deps.base import get_settings


settings = get_settings()

SCHEMA = "scheduling"
TABLE_ARGS = {"schema": SCHEMA} if settings.use_schema else {}
USER_FK = f"{SCHEMA}.scheduling_user.id" if settings.use_schema else "scheduling_user.id"
TEAM_FK = f"{SCHEMA}.scheduling_team.id" if settings.use_schema else "scheduling_team.id"
MEETING_FK = f"{SCHEMA}.scheduling_meeting.id" if settings.use_schema else "scheduling_meeting.id"


class SchedulingUserOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "scheduling_user"
    __table_args__ = TABLE_ARGS

    username: Mapped[str] = mapped_column(String, nullable=True)


class SchedulingTeamOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "scheduling_team"
    __table_args__ = TABLE_ARGS


class SchedulingMemberOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "scheduling_member"
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(USER_FK), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey(TEAM_FK), nullable=False)
    is_manager: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class SchedulingMeetingOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "scheduling_meeting"
    __table_args__ = TABLE_ARGS

    organizer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(USER_FK), nullable=False
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TEAM_FK), nullable=False
    )
    start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    is_cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class SchedulingMeetingParticipantOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "scheduling_meeting_participant"
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(USER_FK), nullable=False)
    meeting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(MEETING_FK), nullable=False
    )
