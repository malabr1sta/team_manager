from app.core.entity import Entity
from app.core.shared.models.users import BaseUser
from app.core.custom_types import ids, calendar_type

from datetime import datetime


class CalendarUser(BaseUser):
    ...


class CalendarEvent(Entity):
    """
    Represents a single calendar event for a user.

    Attributes:
        user_id: ID of the user who owns the event.
        id: Unique ID of the calendar event.
        type: Role/type of the event (task, meeting, etc.).
        title: Title of the event.
        description: Description of the event.
        time: Date and time of the event.
        reference_id: ID of the related task or meeting.
        cancelled: Whether the event is cancelled.
    """

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


class Calendar(Entity):
    """
    In-memory calendar for storing and accessing user events.

    Note:
        Calendar instances are not intended to be persisted in a database.
        Used only for filtering events by day or month.
    """

    def __init__(
        self, user_id: ids.UserId,
        calendar_events: list[CalendarEvent]

    ):
        self._user_id = user_id
        self._calendar_events = calendar_events

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
