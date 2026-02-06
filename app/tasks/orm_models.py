from app.core.database import Base, IdMixin, TimestampMixin
from app.core.custom_types import task_status
from datetime import datetime

from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column
)
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
)


SCHEMA = "tasks"
TASK_FK = f"{SCHEMA}.task.id" if Base.USE_SCHEMA else "tasks.id"
TEAM_FK = f"{SCHEMA}.task_teams.id" if Base.USE_SCHEMA else "task_teams.id"
USER_FK = f"{SCHEMA}.tasks_user.id" if Base.USE_SCHEMA else "tasks_user.id"
TABLE_ARGS = {"schema": SCHEMA} if Base.USE_SCHEMA else {}


class TaskUserOrm(Base, TimestampMixin):
    __tablename__ = 'tasks_user'
    __table_args__ = TABLE_ARGS

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    username: Mapped[str] = mapped_column(String)


class TaskMemberOrm(Base, IdMixin):
    __tablename__ = "task_member"
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(USER_FK)
    )
    team_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TEAM_FK)
    )

    role: Mapped[str] = mapped_column(String)


class TaskTeamOrm(Base, TimestampMixin):
    __tablename__ = 'task_teams'
    __table_args__ = TABLE_ARGS

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    members = relationship(
        TaskMemberOrm,
        foreign_keys="TaskMemberOrm.team_id",
        lazy="selectin",
        cascade="all, delete-orphan"
    )


class CommentOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = 'task_comment'
    __table_args__ = TABLE_ARGS

    author_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(USER_FK),
        nullable=False,
    )
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(TASK_FK),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(String)
    team_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey(TEAM_FK), nullable=True
    )


class TaskOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "tasks"
    __table_args__ = TABLE_ARGS

    supervisor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(USER_FK),
        nullable=False,
    )

    executor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(USER_FK),
        nullable=True,
    )

    team_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(TEAM_FK),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[task_status.TaskStatus] = mapped_column(
        Enum(task_status.TaskStatus, name="task_status"),
        nullable=False,
        default=task_status.TaskStatus.OPEN,
    )

    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
