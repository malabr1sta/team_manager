from app.core.repositories.descriptor import LazyRepo
from app.core.unit_of_work import AbstractSqlRepositoryProvider, SQLAlchemyUnitOfWork
from app.scheduling import repository as repo


class SchedulingRepositoryProvider(AbstractSqlRepositoryProvider):
    user = LazyRepo(repo.SQLAlchemySchedulingUserRepository)
    team = LazyRepo(repo.SQLAlchemySchedulingTeamRepository)
    member = LazyRepo(repo.SQLAlchemySchedulingMemberRepository)
    meeting = LazyRepo(repo.SQLAlchemySchedulingMeetingRepository)


class SchedulingSQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[SchedulingRepositoryProvider]
):
    ...
