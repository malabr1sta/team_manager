from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateMeetingCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    team_id: int = Field(..., gt=0)
    start: datetime
    end: datetime
    description: str = Field(default="", max_length=1000)
    actor_user_id: int | None = Field(default=None, gt=0)


class MeetingParticipantReadDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    meeting_id: int


class MeetingReadDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    organizer_id: int
    team_id: int
    start: datetime
    end: datetime
    description: str
    is_cancelled: bool
    participants: list[MeetingParticipantReadDTO]


class MeetingListDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[MeetingReadDTO]
    total: int
    limit: int
    offset: int
