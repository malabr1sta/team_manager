from dataclasses import dataclass
from datetime import datetime

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class MeetingCreated(DomainEvent):
    meeting_id: int
    team_id: int
    organizer_id: int
    participant_ids: list[int]
    start: datetime
    end: datetime
    description: str
    is_cancelled: bool


@dataclass(frozen=True)
class MeetingUpdated(DomainEvent):
    meeting_id: int
    team_id: int
    organizer_id: int
    participant_ids: list[int]
    previous_participant_ids: list[int]
    start: datetime
    end: datetime
    description: str
    is_cancelled: bool


@dataclass(frozen=True)
class MeetingCancelled(DomainEvent):
    meeting_id: int
    team_id: int
    organizer_id: int
    participant_ids: list[int]
