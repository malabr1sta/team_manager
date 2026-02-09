from app.core.shared.events import teams as team_event
from app.core.repositories import tasks
from app.core.custom_types import ids, session_factory
from app.core.infrastructure.event import EventHandler
from app.tasks.models import Team

from typing import Type


class TeamCreatedHandler(EventHandler[team_event.TeamCreated]):
    """Handler for TeamCreated event."""

    def __init__(
            self,
            type_repo: Type[tasks.TaskTeamProtocol],
            session_factory: session_factory.AsyncSessionFactory
    ):
        self.type_repo = type_repo
        self.session_factory = session_factory

    async def handle(self, event: team_event.TeamCreated) -> None:
        """Create TaskTeam when Team is created."""
        async with self.session_factory() as session:
            repo = self.type_repo(session)
            team = Team(ids.TeamId(event.team_id), [])
            await repo.save(team)
