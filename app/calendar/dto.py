from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, Field


class CalendarEventReadDTO(BaseModel):
    """Represents one calendar event item."""

    model_config = ConfigDict(frozen=True)

    id: int
    user_id: int
    event_type: str
    title: str
    description: str
    time: datetime
    reference_id: int
    cancelled: bool


class CalendarDayQuery(BaseModel):
    """Represents day calendar query."""

    model_config = ConfigDict(frozen=True)

    day: date


class CalendarMonthQuery(BaseModel):
    """Represents month calendar query."""

    model_config = ConfigDict(frozen=True)

    year: int = Field(..., ge=1970, le=3000)
    month: int = Field(..., ge=1, le=12)


class CalendarEventsDTO(BaseModel):
    """Represents calendar response payload."""

    model_config = ConfigDict(frozen=True)

    items: list[CalendarEventReadDTO]
    total: int
