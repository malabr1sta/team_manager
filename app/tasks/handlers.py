from app.core.shared.events import teams as team_event
from app.core.custom_types import ids, role
from app.core.infrastructure.event import EventHandler
from app.tasks.models import Team, MemberTask
from app.tasks.unit_of_work import (
        TaskSQLAlchemyUnitOfWork
)


class TeamCreatedHandler(EventHandler[team_event.TeamCreated]):
    """Handler for TeamCreated event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow


    async def handle(self, event: team_event.TeamCreated) -> None:
        """Create TaskTeam when Team is created."""
        async with self.uow as uow:
            team = Team(ids.TeamId(event.team_id), [])
            await uow.repos.team.save(team)
            await uow.commit()


class MemblerAddTeamHandler(EventHandler[team_event.MemberAddTeam]):
    """Handler for MemblerAddTeam event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow


    async def handle(self, event: team_event.MemberAddTeam) -> None:
        """Add member in Team."""
        async with self.uow as uow:
            member = MemberTask(
                user_id=ids.UserId(event.user_id),
                team_id=ids.TeamId(event.team_id),
                role=role.UserTaskRole(event.role)
            )
            await uow.repos.member.save(member)
            await uow.commit()

