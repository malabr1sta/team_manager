from dataclasses import dataclass
from datetime import datetime

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class TeamCreated(DomainEvent):
    """Event: Team was created in Team context."""
    team_id: int
