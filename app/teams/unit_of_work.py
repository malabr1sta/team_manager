from typing import TYPE_CHECKING

from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,

)
from app.core.repositories.descriptor import LazyRepo
from app.core.repositories.teams import (
    TeamUserProtocol,
    MemberRepositoryProtocol,
    TeamRepositoryProtocol
)
from app.teams import repository as repo


class TeamRepositoryProvider(AbstractSqlRepositoryProvider):
    """Task's interface for SQL repository providers."""
    if TYPE_CHECKING:
        user: TeamUserProtocol
        member: MemberRepositoryProtocol
        team: TeamRepositoryProtocol
    else:
        user = LazyRepo(repo.SQLAlchemyUserRepository)
        member = LazyRepo(repo.SQLAlchemyMemberRepository)
        team = LazyRepo(repo.SQLAlchemyTeamRepository)


class TeamSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[TeamRepositoryProvider]):
    ...
