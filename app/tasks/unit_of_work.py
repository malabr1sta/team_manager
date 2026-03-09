from typing import TYPE_CHECKING

from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,

)
from app.core.repositories.descriptor import LazyRepo
from app.core.repositories.tasks import (
    TaskUserProtocol,
    TaskMemberProtocol,
    TaskTeamProtocol,
    TaskCommentProtocol,
    TaskProtocol,
)
from app.tasks import repository as repo


class TaskRepositoryProvider(AbstractSqlRepositoryProvider):
    """Task's interface for SQL repository providers."""
    if TYPE_CHECKING:
        user: TaskUserProtocol
        member: TaskMemberProtocol
        team: TaskTeamProtocol
        comment: TaskCommentProtocol
        task: TaskProtocol
    else:
        user = LazyRepo(repo.SQLAlchemyTaskUserRepository)
        member = LazyRepo(repo.SQLAlchemyTaskMemberRepository)
        team = LazyRepo(repo.SQLAlchemyTeamRepository)
        comment = LazyRepo(repo.SQLAlchemyTaskCommentRepository)
        task = LazyRepo(repo.SQLAlchemyTaskRepository)


class TaskSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[TaskRepositoryProvider]):
    ...
