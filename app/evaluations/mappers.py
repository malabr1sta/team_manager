from typing import cast

from app.core.custom_types import grade as grade_type, ids
from app.evaluations import models
from app.evaluations.orm_models import EvaluationOrm, EvaluationTaskOrm, EvaluationUserOrm


class EvaluationUserMapper:
    @staticmethod
    def to_domain(orm: EvaluationUserOrm) -> models.User:
        return models.User(
            id=ids.UserId(orm.id),
            username=orm.username or "",
        )

    @staticmethod
    def to_orm(user: models.User) -> EvaluationUserOrm:
        return EvaluationUserOrm(
            id=user.id,
            username=user.username,
        )

    @staticmethod
    def update_orm(orm: EvaluationUserOrm, user: models.User) -> None:
        orm.username = user.username


class EvaluationTaskMapper:
    @staticmethod
    def to_domain(orm: EvaluationTaskOrm) -> models.Task:
        executor_id = ids.UserId(orm.executor_id) if orm.executor_id else ids.UserId(0)
        return models.Task(
            id=ids.TaskId(orm.id),
            team_id=ids.TeamId(orm.team_id),
            supervisor_id=ids.UserId(orm.supervisor_id),
            executor_id=executor_id,
            status=orm.status,
        )

    @staticmethod
    def to_orm(task: models.Task) -> EvaluationTaskOrm:
        return EvaluationTaskOrm(
            id=task.id,
            team_id=task.team_id,
            supervisor_id=task.supervisor_id,
            executor_id=task.executor_id,
            status=task.status,
        )

    @staticmethod
    def update_orm(orm: EvaluationTaskOrm, task: models.Task) -> None:
        orm.team_id = task.team_id
        orm.supervisor_id = task.supervisor_id
        orm.executor_id = task.executor_id
        orm.status = task.status


class EvaluationMapper:
    @staticmethod
    def to_domain(orm: EvaluationOrm) -> models.Evaluation:
        return models.Evaluation(
            user_id=ids.UserId(orm.user_id),
            team_id=ids.TeamId(orm.team_id),
            task_id=ids.TaskId(orm.task_id),
            grade=cast(grade_type.Grade, orm.grade),
            created_at=orm.created_dttm,
        )

    @staticmethod
    def to_orm(evaluation: models.Evaluation) -> EvaluationOrm:
        return EvaluationOrm(
            user_id=evaluation.user_id,
            team_id=evaluation.team_id,
            task_id=evaluation.task_id,
            grade=evaluation.grade,
        )
