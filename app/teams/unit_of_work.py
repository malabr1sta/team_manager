from app.core.unit_of_work import SQLAlchemyUnitOfWork

from app.teams import repository as repo


class TeamSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork):
    REPOS = {
        "user": repo.SQLAlchemyUserRepository,
        "member": repo.SQLAlchemyMemberRepository,
        "team": repo.SQLAlchemyTeamRepository
    }
