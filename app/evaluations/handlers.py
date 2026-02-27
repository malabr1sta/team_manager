from app.core.custom_types import ids, task_status
from app.core.infrastructure.event import EventHandler
from app.core.shared.events import tasks as task_event
from app.core.shared.handlers.users import UserCreatedHandler
from app.evaluations.models import Task, User
from app.evaluations.unit_of_work import EvaluationSQLAlchemyUnitOfWork


class EvaluationUserCreatedHandler(
    UserCreatedHandler[EvaluationSQLAlchemyUnitOfWork, type[User]]
):
    ...


class EvaluationTaskCreatedHandler(EventHandler[task_event.TaskCreated]):
    def __init__(self, uow: EvaluationSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: task_event.TaskCreated) -> None:
        async with self.uow as uow:
            task = Task(
                id=ids.TaskId(event.task_id),
                team_id=ids.TeamId(event.team_id),
                supervisor_id=ids.UserId(event.supervisor_id),
                executor_id=ids.UserId(event.executor_id or 0),
                status=task_status.TaskStatus(event.status),
            )
            await uow.repos.task.save(task)
            await uow.commit()


class EvaluationTaskUpdatedHandler(EventHandler[task_event.TaskUpdated]):
    def __init__(self, uow: EvaluationSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: task_event.TaskUpdated) -> None:
        async with self.uow as uow:
            task = Task(
                id=ids.TaskId(event.task_id),
                team_id=ids.TeamId(event.team_id),
                supervisor_id=ids.UserId(event.supervisor_id),
                executor_id=ids.UserId(event.executor_id or 0),
                status=task_status.TaskStatus(event.status),
            )
            await uow.repos.task.save(task)
            await uow.commit()
