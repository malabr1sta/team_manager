from dataclasses import dataclass

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class TeamCreated(DomainEvent):
    """Event: Team was created in Team context."""
    team_id: int
    user_id: int


@dataclass(frozen=True)
class MemberAddTeam(DomainEvent):
    """Event: Member add in Team context."""
    team_id: int
    user_id: int
    role: str


@dataclass(frozen=True)
class MemberRemoveTeam(DomainEvent):
    """Event: Member remove in Team context."""
    team_id: int
    user_id: int
    role: str


@dataclass(frozen=True)
class MemberChangeRole(DomainEvent):
    """Event: Member change role in Team context."""
    team_id: int
    user_id: int
    role: str
