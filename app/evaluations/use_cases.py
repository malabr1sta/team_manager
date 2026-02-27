from datetime import datetime

from fastapi import HTTPException

from app.core.custom_types import ids
from app.evaluations import custom_exception, dto, management
from app.evaluations.models import Evaluation
from app.evaluations.unit_of_work import EvaluationSQLAlchemyUnitOfWork


def map_evaluation_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, custom_exception.EvaluationSupervisorException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.EvaluationException):
        return HTTPException(400, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(400, str(exc))
    if isinstance(exc, HTTPException):
        return exc
    return HTTPException(400, str(exc))


def _to_evaluation_dto(item: Evaluation) -> dto.EvaluationReadDTO:
    return dto.EvaluationReadDTO(
        user_id=item.user_id,
        team_id=item.team_id,
        task_id=item.task_id,
        grade=item.grade,
        created_at=item.created_at,
    )


class CreateEvaluationUseCase:
    def __init__(self, uow: EvaluationSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        command: dto.CreateEvaluationCommand,
    ) -> dto.EvaluationReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        if command.task_id is None:
            raise ValueError("task_id is required")

        task = await self.uow.repos.task.get_by_id(command.task_id)
        if task is None:
            raise HTTPException(404, "Task not found")

        evaluation = management.create_evaluation(
            supervisor_id=ids.UserId(command.actor_user_id),
            task=task,
            grade=command.grade,
        )
        await self.uow.repos.evaluation.save(evaluation)
        await self.uow.commit()
        return _to_evaluation_dto(evaluation)


class ListMyEvaluationUseCase:
    def __init__(self, uow: EvaluationSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        user_id: int,
        team_id: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dto.EvaluationListDTO:
        evaluations = await self.uow.repos.evaluation.get_by_user(
            user_id=user_id,
            team_id=team_id,
            start=start,
            end=end,
        )
        items = [_to_evaluation_dto(item) for item in evaluations]
        return dto.EvaluationListDTO(items=items, total=len(items))


class GetAverageEvaluationUseCase:
    def __init__(self, uow: EvaluationSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        user_id: int,
        team_id: int,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> dto.EvaluationAverageDTO:
        user = await self.uow.repos.user.get_by_id(user_id)
        if user is None:
            raise HTTPException(404, "User not found")
        average = user.average_grade(
            team_id=ids.TeamId(team_id),
            start=start,
            end=end,
        )
        return dto.EvaluationAverageDTO(average=average)
