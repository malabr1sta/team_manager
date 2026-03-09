from typing import Protocol, runtime_checkable

from app.scheduling.models import Meeting, MemberTeam, Team, User


@runtime_checkable
class SchedulingUserProtocol(Protocol):
    """Protocol user's repository"""

    async def get_by_id(self, id: int) -> User | None:
        ...

    async def save(self, domain: User) -> None:
        ...


@runtime_checkable
class SchedulingTeamProtocol(Protocol):
    """Protocol team's repository"""

    async def get_by_id(self, id: int) -> Team | None:
        ...

    async def save(self, domain: Team) -> None:
        ...


@runtime_checkable
class SchedulingMemberProtocol(Protocol):
    """Protocol member's repository"""

    async def get_by_user_and_team(
        self,
        user_id: int,
        team_id: int
    ) -> MemberTeam | None:
        ...

    async def save(self, domain: MemberTeam) -> None:
        ...

    async def delete(self, user_id: int, team_id: int) -> None:
        ...


@runtime_checkable
class SchedulingMeetingProtocol(Protocol):
    """Protocol meeting's repository"""

    async def get_by_id(self, id: int) -> Meeting | None:
        ...

    async def get_by_team(self, team_id: int) -> list[Meeting]:
        ...

    async def save(self, domain: Meeting) -> None:
        ...


@runtime_checkable
class SchedulingRepos(Protocol):
    user: SchedulingUserProtocol
    team: SchedulingTeamProtocol
    member: SchedulingMemberProtocol
    meeting: SchedulingMeetingProtocol
