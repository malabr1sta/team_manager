from typing import Protocol, runtime_checkable

from app.teams.models import Team


@runtime_checkable
class TeamRepositoryProtocol(Protocol):
    """Protocol team's repository"""

    async def get_by_id(self, team_id: int) -> Team | None:
        ...

    async def save(self, team: Team) -> Team:
        ...

    async def delete(self, team_id: int) -> None:
        ...
