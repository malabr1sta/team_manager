from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,

)
from app.tasks import repository as repo

from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepositoryProvider(AbstractSqlRepositoryProvider):
    """Task's interface for SQL repository providers."""
    def __init__(self, session: AsyncSession, uow):

        self.user: repo.SQLAlchemyTaskUserRepository = (
            repo.SQLAlchemyTaskUserRepository(session, uow)
        )
        self.member: repo.SQLAlchemyTaskMemberRepository = (
            repo.SQLAlchemyTaskMemberRepository(session, uow)
        )
        self.team: repo.SQLAlchemyTeamRepository = (
            repo.SQLAlchemyTeamRepository(session, uow)
        )
        self.comment: repo.SQLAlchemyTaskCommentRepository = (
            repo.SQLAlchemyTaskCommentRepository(session, uow)
        )
        self.task: repo.SQLAlchemyTaskRepository = (
            repo.SQLAlchemyTaskRepository(session, uow)
        )


class TaskSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[TaskRepositoryProvider]):
    ...
