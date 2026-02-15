from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,

)
from app.core.repositories.descriptor import LazyRepo
from app.teams import repository as repo


class TeamRepositoryProvider(AbstractSqlRepositoryProvider):
    """Task's interface for SQL repository providers."""
    user = LazyRepo(repo.SQLAlchemyUserRepository)
    member = LazyRepo(repo.SQLAlchemyMemberRepository)
    team = LazyRepo(repo.SQLAlchemyTeamRepository)


class TeamSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[TeamRepositoryProvider]):
    ...
