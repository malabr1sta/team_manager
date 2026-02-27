from fastapi import HTTPException

from app.core.custom_types import ids, task_patch, task_status
from app.tasks import custom_exception, dto, management
from app.tasks.models import Task
from app.tasks.unit_of_work import TaskSQLAlchemyUnitOfWork


def map_task_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, custom_exception.TaskSupervisorException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.TaskMemberException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.CommentException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.TaskDeadlineException):
        return HTTPException(400, str(exc))
    if isinstance(exc, custom_exception.TaskMemberNotFoundException):
        return HTTPException(404, str(exc))
    if isinstance(exc, custom_exception.TeamNotFoundException):
        return HTTPException(404, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(400, str(exc))
    if isinstance(exc, HTTPException):
        return exc
    return HTTPException(400, str(exc))


def _to_task_dto(task: Task) -> dto.TaskReadDTO:
    deadline = task.deadline
    if deadline is None:
        raise HTTPException(400, "Task deadline is missing")
    return dto.TaskReadDTO(
        id=task.id or 0,
        team_id=task.team_id,
        supervisor_id=task.supervisor_id,
        executor_id=task.executor_id,
        title=task.title,
        description=task.description,
        status=task.status.value,
        deadline=deadline,
        created_at=task.created_at,
        updated_at=task.updated_at,
        deleted=task.deleted,
    )


class CreateTaskUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.CreateTaskCommand) -> dto.TaskReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        team = await self.uow.repos.team.get_by_id(command.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        task = management.create_task(
            ids.UserId(command.actor_user_id),
            team,
            command.deadline,
            command.title,
            command.description,
        )
        await self.uow.repos.task.save(task)
        await self.uow.commit()
        return _to_task_dto(task)


class ReadTaskUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, task_id: int, actor_user_id: int) -> dto.TaskReadDTO:
        task = await self.uow.repos.task.get_by_id(task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        if task.team_id is None:
            raise HTTPException(400, "Task without team is not supported")
        user_memberships = await self.uow.repos.member.get_by_user_and_team(
            actor_user_id, task.team_id
        )
        if not user_memberships and task.supervisor_id != actor_user_id and task.executor_id != actor_user_id:
            raise HTTPException(403, "No access to task")
        return _to_task_dto(task)


class ListTaskUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        *,
        actor_user_id: int,
        team_id: int | None,
        assigned_only: bool,
        limit: int,
        offset: int,
    ) -> dto.TaskListDTO:
        if assigned_only:
            tasks = await self.uow.repos.task.get_by_executor(actor_user_id)
        elif team_id is not None:
            user_memberships = await self.uow.repos.member.get_by_user_and_team(
                actor_user_id, team_id
            )
            if not user_memberships:
                raise HTTPException(403, "No access to team tasks")
            tasks = await self.uow.repos.task.get_by_team(team_id)
        else:
            supervisor_tasks = await self.uow.repos.task.get_by_supervisor(actor_user_id)
            executor_tasks = await self.uow.repos.task.get_by_executor(actor_user_id)
            supervisor_ids = {task.id for task in supervisor_tasks}
            tasks = supervisor_tasks + [
                task for task in executor_tasks if task.id not in supervisor_ids
            ]

        items = [_to_task_dto(task) for task in tasks]
        paged_items = items[offset: offset + limit]
        return dto.TaskListDTO(
            items=paged_items,
            total=len(items),
            limit=limit,
            offset=offset,
        )


class AssignExecutorUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.AssignExecutorCommand) -> dto.TaskReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        task = await self.uow.repos.task.get_by_id(command.task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        if task.team_id is None:
            raise HTTPException(400, "Task without team is not supported")
        team = await self.uow.repos.team.get_by_id(task.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        action = management.ActionAppointmentExecutorTask(
            task, ids.UserId(command.actor_user_id)
        )
        action.execute(ids.UserId(command.executor_id), team)
        await self.uow.repos.task.save(task)
        await self.uow.commit()
        return _to_task_dto(task)


class UpdateTaskUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.UpdateTaskCommand) -> dto.TaskReadDTO:
        if command.task_id is None:
            raise ValueError("task_id is required")
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        task = await self.uow.repos.task.get_by_id(command.task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        action = management.ActionUpdateTask(task, ids.UserId(command.actor_user_id))
        update_payload: task_patch.TaskUpdateArgs = {}
        if command.title is not None:
            update_payload["title"] = command.title
        if command.description is not None:
            update_payload["description"] = command.description
        if command.status is not None:
            update_payload["status"] = task_status.TaskStatus(command.status)
        if command.deleted is not None:
            update_payload["deleted"] = command.deleted
        action.execute(**update_payload)
        await self.uow.repos.task.save(task)
        await self.uow.commit()
        return _to_task_dto(task)


class AddCommentUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.AddCommentCommand) -> dto.CommentReadDTO:
        if command.task_id is None:
            raise ValueError("task_id is required")
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        task = await self.uow.repos.task.get_by_id(command.task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        if task.team_id is None:
            raise HTTPException(400, "Task without team is not supported")
        team = await self.uow.repos.team.get_by_id(task.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        action = management.ActionCreateComment(
            team, ids.UserId(command.actor_user_id)
        )
        comment = action.execute(
            ids.TaskId(command.task_id),
            command.text,
            ids.CommentId(0),
        )
        await self.uow.repos.comment.save(comment)
        await self.uow.commit()
        return dto.CommentReadDTO(
            id=comment.id or 0,
            task_id=comment.task_id,
            author_id=comment.author_id,
            text=comment.text,
            created_at=comment.created_at,
        )


class ListCommentUseCase:
    def __init__(self, uow: TaskSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self, task_id: int, actor_user_id: int
    ) -> list[dto.CommentReadDTO]:
        task = await self.uow.repos.task.get_by_id(task_id)
        if task is None:
            raise HTTPException(404, "Task not found")
        if task.team_id is not None:
            memberships = await self.uow.repos.member.get_by_user_and_team(
                actor_user_id, task.team_id
            )
            if not memberships and task.supervisor_id != actor_user_id and task.executor_id != actor_user_id:
                raise HTTPException(403, "No access to comments")
        comments = await self.uow.repos.comment.get_by_task_id(task_id)
        return [
            dto.CommentReadDTO(
                id=comment.id or 0,
                task_id=comment.task_id,
                author_id=comment.author_id,
                text=comment.text,
                created_at=comment.created_at,
            )
            for comment in comments
        ]
