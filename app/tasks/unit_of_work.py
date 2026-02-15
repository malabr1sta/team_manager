from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,

)
from app.core.repositories.descriptor import LazyRepo
from app.tasks import repository as repo


class TaskRepositoryProvider(AbstractSqlRepositoryProvider):
    """Task's interface for SQL repository providers."""
    user = LazyRepo(repo.SQLAlchemyTaskUserRepository)
    member = LazyRepo(repo.SQLAlchemyTaskMemberRepository)
    team = LazyRepo(repo.SQLAlchemyTeamRepository)
    comment = LazyRepo(repo.SQLAlchemyTaskCommentRepository)
    task = LazyRepo(repo.SQLAlchemyTaskRepository)


class TaskSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[TaskRepositoryProvider]):
    ...
