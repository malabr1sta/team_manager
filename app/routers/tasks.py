from fastapi import APIRouter, Query, status

from app.deps.task import TaskUoW
from app.deps.user import UserDepend
from app.tasks import dto, use_cases


tasks_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@tasks_router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(
    command_body: dto.CreateTaskCommand,
    user: UserDepend,
    uow: TaskUoW,
):
    command = command_body.model_copy(update={"actor_user_id": user.id})
    try:
        return await use_cases.CreateTaskUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.get("/{task_id}")
async def get_task(
    task_id: int,
    user: UserDepend,
    uow: TaskUoW,
):
    try:
        return await use_cases.ReadTaskUseCase(uow).execute(task_id, user.id)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.get("")
async def list_tasks(
    user: UserDepend,
    uow: TaskUoW,
    team_id: int | None = Query(default=None, gt=0),
    assigned_only: bool = False,
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        return await use_cases.ListTaskUseCase(uow).execute(
            actor_user_id=user.id,
            team_id=team_id,
            assigned_only=assigned_only,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.patch("/{task_id}")
async def update_task(
    task_id: int,
    command_body: dto.UpdateTaskCommand,
    user: UserDepend,
    uow: TaskUoW,
):
    command = command_body.model_copy(
        update={"task_id": task_id, "actor_user_id": user.id}
    )
    try:
        return await use_cases.UpdateTaskUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.post("/{task_id}/executor/{executor_id}")
async def assign_executor(
    task_id: int,
    executor_id: int,
    user: UserDepend,
    uow: TaskUoW,
):
    command = dto.AssignExecutorCommand(
        task_id=task_id,
        executor_id=executor_id,
        actor_user_id=user.id,
    )
    try:
        return await use_cases.AssignExecutorUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.post("/{task_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: int,
    command_body: dto.AddCommentCommand,
    user: UserDepend,
    uow: TaskUoW,
):
    command = command_body.model_copy(
        update={"task_id": task_id, "actor_user_id": user.id}
    )
    try:
        return await use_cases.AddCommentUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)


@tasks_router.get("/{task_id}/comments")
async def list_comments(
    task_id: int,
    user: UserDepend,
    uow: TaskUoW,
):
    try:
        return await use_cases.ListCommentUseCase(uow).execute(task_id, user.id)
    except Exception as exc:
        raise use_cases.map_task_exception(exc)
