import pytest
from datetime import datetime

from app.calendar.models import Calendar, CalendarEvent
from app.core.custom_types import ids, calendar_type


@pytest.fixture
def events():
    return [
        CalendarEvent(
            user_id=ids.UserId(1),
            id=ids.CalendarEventId(1),
            type=calendar_type.CalendarEventType.TASK,
            title="Event 1",
            description="Test",
            time=datetime(2026, 1, 10, 10, 0),
            reference_id=ids.TaskId(1),
            cancelled=None,
        ),
        CalendarEvent(
            user_id=ids.UserId(1),
            id=ids.CalendarEventId(2),
            type=calendar_type.CalendarEventType.MEETING,
            title="Event 2",
            description="Test",
            time=datetime(2026, 1, 10, 15, 0),
            reference_id=ids.MeetingId(1),
            cancelled=True,
        ),
        CalendarEvent(
            user_id=ids.UserId(1),
            id=ids.CalendarEventId(3),
            type=calendar_type.CalendarEventType.TASK,
            title="Event 3",
            description="Test",
            time=datetime(2026, 1, 15, 12, 0),
            reference_id=ids.TaskId(1),
            cancelled=None,
        ),
    ]


@pytest.fixture
def calendar(events):
    return Calendar(user_id=ids.UserId(1), calendar_events=events)

