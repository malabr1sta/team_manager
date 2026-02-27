from app.core.entity import Entity
from app.core.shared.models.users import BaseUser
from app.core.custom_types import ids, calendar_type

from datetime import datetime


class CalendarUser(BaseUser):
    ...


class CalendarEvent(Entity):
    """Represents one user calendar event."""

    def __init__(
        self,
        user_id: ids.UserId,
        id: ids.CalendarEventId,
        type: calendar_type.CalendarEventType,
        description: str,
        title: str,
        time: datetime,
        reference_id: ids.TaskId | ids.MeetingId,
        cancelled: bool | None
    ):
        self._user_id = user_id
        self._id = id
        self._type = type
        self._title = title
        self._description = description
        self._time = time
        self._reference_id = reference_id
        self._cancelled = cancelled

    @property
    def id(self) -> ids.CalendarEventId:
        return self._id

    @property
    def user_id(self) -> ids.UserId:
        return self._user_id

    @property
    def type(self) -> calendar_type.CalendarEventType:
        return self._type

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def reference_id(self) -> ids.TaskId | ids.MeetingId:
        return self._reference_id

    @property
    def cancelled(self) -> bool:
        return bool(self._cancelled)

    def mark_cancelled(self) -> None:
        self._cancelled = True


class Calendar(Entity):
    """Stores and filters user calendar events."""

    def __init__(
        self, user_id: ids.UserId,
        calendar_events: list[CalendarEvent]

    ):
        self._user_id = user_id
        self._calendar_events = calendar_events

    @property
    def user_id(self) -> ids.UserId:
        return self._user_id

    @property
    def calendar_events(self) -> tuple[CalendarEvent, ...]:
        return tuple(self._calendar_events)

    def events_for_day(self, date: datetime) -> list[CalendarEvent]:
        """Returns a list of events for a specific day."""
        day_str = date.strftime('%Y-%m-%d')
        return [
            e for e in self._calendar_events
            if e._time.strftime('%Y-%m-%d') == day_str and not e._cancelled
        ]

    def events_for_month(self, year: int, month: int) -> list[CalendarEvent]:
        """Returns a list of events for a month"""
        return [
            e for e in self._calendar_events
            if (e._time.year == year
                and e._time.month == month
                and not e._cancelled)
        ]
