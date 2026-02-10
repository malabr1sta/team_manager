from sqlalchemy.ext.asyncio import AsyncSession

from app.core.shared.events import teams as team_event
from app.core.repositories import tasks
from app.core.custom_types import ids
from app.core.infrastructure.event import EventHandler
from app.tasks.models import Team

from typing import Type



class TeamCreatedHandler(EventHandler[team_event.TeamCreated]):
    """Handler for TeamCreated event."""

    def __init__(
            self,
            type_repo: Type[tasks.TaskTeamProtocol],
    ):
        self.type_repo = type_repo

    async def handle(
        self,
        event: team_event.TeamCreated,
        session: AsyncSession
    ) -> None:
        """Create TaskTeam when Team is created."""
        repo = self.type_repo(session)
        team = Team(ids.TeamId(event.team_id), [])
        await repo.save(team)
