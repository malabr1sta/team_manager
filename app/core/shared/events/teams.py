from dataclasses import dataclass

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class TeamCreated(DomainEvent):
    """Event: Team was created in Team context."""
    team_id: int
    user_id: int


class MemberEvent(DomainEvent):
    pass


@dataclass(frozen=True)
class MemberAddTeam(MemberEvent):
    """Event: Member add in Team context."""
    team_id: int
    user_id: int
    role: str


@dataclass(frozen=True)
class MemberRemoveTeam(MemberEvent):
    """Event: Member remove in Team context."""
    team_id: int
    user_id: int
    role: str


@dataclass(frozen=True)
class MemberChangeRole(MemberEvent):
    """Event: Member change role in Team context."""
    team_id: int
    user_id: int
    new_role: str
    old_role: str
