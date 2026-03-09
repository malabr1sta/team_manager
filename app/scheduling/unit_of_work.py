from typing import TYPE_CHECKING

from app.core.repositories.descriptor import LazyRepo
from app.core.repositories.scheduling import (
    SchedulingUserProtocol,
    SchedulingTeamProtocol,
    SchedulingMemberProtocol,
    SchedulingMeetingProtocol,
)
from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,
)
from app.scheduling import repository as repo


class SchedulingRepositoryProvider(AbstractSqlRepositoryProvider):
    if TYPE_CHECKING:
        user: SchedulingUserProtocol
        team: SchedulingTeamProtocol
        member: SchedulingMemberProtocol
        meeting: SchedulingMeetingProtocol
    else:
        user = LazyRepo(repo.SQLAlchemySchedulingUserRepository)
        team = LazyRepo(repo.SQLAlchemySchedulingTeamRepository)
        member = LazyRepo(repo.SQLAlchemySchedulingMemberRepository)
        meeting = LazyRepo(repo.SQLAlchemySchedulingMeetingRepository)


class SchedulingSQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[SchedulingRepositoryProvider]
):
    ...
