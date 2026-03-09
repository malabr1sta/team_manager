from typing import Protocol, runtime_checkable

from app.teams.models import Team, Member, User


@runtime_checkable
class TeamUserProtocol(Protocol):
    """Protocol user's repository"""

    async def save(self, id: int):
        ...

    async def get_by_id(self, id: int) -> User | None:
        ...


@runtime_checkable
class TeamRepositoryProtocol(Protocol):
    """Protocol team's repository"""

    async def get_by_id(self, team_id: int) -> Team | None:
        ...

    async def save(self, team: Team) -> Team:
        ...


@runtime_checkable
class MemberRepositoryProtocol(Protocol):
    """Protocol member's repository"""

    async def get_by_user(
        self, user_id: int
    ) -> list[Member]:
        ...

    async def get_by_user_and_team(
        self,
        user_id: int,
        team_id: int,
    ) -> Member | None:
        ...

    async def save(self, member: Member) -> Member:
        ...


@runtime_checkable
class TeamRepos(Protocol):
    team: TeamRepositoryProtocol
    member: MemberRepositoryProtocol
    user: TeamUserProtocol
