from app.core.shared.events import teams as team_event
from app.core.custom_types import ids
from app.core.infrastructure.event import EventHandler
from app.tasks.models import Team
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
