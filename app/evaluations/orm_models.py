from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.custom_types import task_status
from app.core.database import Base, IdMixin, TimestampMixin
from app.deps.base import get_settings


settings = get_settings()

SCHEMA = "evaluations"
TABLE_ARGS = {"schema": SCHEMA} if settings.use_schema else {}
USER_FK = f"{SCHEMA}.evaluations_user.id" if settings.use_schema else "evaluations_user.id"
TASK_FK = f"{SCHEMA}.evaluations_task.id" if settings.use_schema else "evaluations_task.id"


class EvaluationUserOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "evaluations_user"
    __table_args__ = TABLE_ARGS

    username: Mapped[str] = mapped_column(String, nullable=True)


class EvaluationTaskOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "evaluations_task"
    __table_args__ = TABLE_ARGS

    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supervisor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    executor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[task_status.TaskStatus] = mapped_column(
        Enum(task_status.TaskStatus, name="evaluations_task_status"),
        nullable=False,
    )


class EvaluationOrm(Base, IdMixin, TimestampMixin):
    __tablename__ = "evaluations"
    __table_args__ = TABLE_ARGS

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(USER_FK), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey(TASK_FK), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
