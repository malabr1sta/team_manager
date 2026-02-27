from datetime import datetime

from fastapi import APIRouter, Query, status

from app.deps.evaluation import EvaluationUoW
from app.deps.user import UserDepend
from app.evaluations import dto, use_cases


evaluations_router = APIRouter(
    prefix="/evaluations",
    tags=["evaluations"],
)


@evaluations_router.post(
    "/tasks/{task_id}",
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation(
    task_id: int,
    command_body: dto.CreateEvaluationCommand,
    user: UserDepend,
    uow: EvaluationUoW,
):
    command = command_body.model_copy(
        update={"task_id": task_id, "actor_user_id": user.id}
    )
    try:
        return await use_cases.CreateEvaluationUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_evaluation_exception(exc)


@evaluations_router.get("/me")
async def list_my_evaluations(
    user: UserDepend,
    uow: EvaluationUoW,
    team_id: int | None = Query(default=None, gt=0),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
):
    try:
        return await use_cases.ListMyEvaluationUseCase(uow).execute(
            user_id=user.id,
            team_id=team_id,
            start=start,
            end=end,
        )
    except Exception as exc:
        raise use_cases.map_evaluation_exception(exc)


@evaluations_router.get("/me/average")
async def my_average_evaluation(
    user: UserDepend,
    uow: EvaluationUoW,
    team_id: int = Query(..., gt=0),
    start: datetime | None = Query(default=None),
    end: datetime | None = Query(default=None),
):
    try:
        return await use_cases.GetAverageEvaluationUseCase(uow).execute(
            user_id=user.id,
            team_id=team_id,
            start=start,
            end=end,
        )
    except Exception as exc:
        raise use_cases.map_evaluation_exception(exc)
