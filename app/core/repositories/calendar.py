from datetime import datetime
from typing import Protocol, runtime_checkable

from app.calendar.models import CalendarEvent, CalendarUser
from app.core.custom_types import calendar_type


@runtime_checkable
class CalendarUserProtocol(Protocol):
    """Protocol user's repository"""

    async def get_by_id(self, id: int) -> CalendarUser | None:
        ...

    async def save(self, domain: CalendarUser) -> None:
        ...


@runtime_checkable
class CalendarEventProtocol(Protocol):
    """Protocol event's repository"""

    async def save(self, domain: CalendarEvent) -> None:
        ...

    async def get_by_user(self, user_id: int) -> list[CalendarEvent]:
        ...

    async def get_by_user_and_reference(
        self,
        user_id: int,
        event_type: calendar_type.CalendarEventType,
        reference_id: int,
    ) -> CalendarEvent | None:
        ...

    async def get_by_reference(
        self,
        event_type: calendar_type.CalendarEventType,
        reference_id: int,
    ) -> list[CalendarEvent]:
        ...

    async def get_by_user_for_day(
        self,
        user_id: int,
        day_start: datetime,
        day_end: datetime,
    ) -> list[CalendarEvent]:
        ...

    async def get_by_user_for_month(
        self,
        user_id: int,
        month_start: datetime,
        month_end: datetime,
    ) -> list[CalendarEvent]:
        ...


@runtime_checkable
class CalendarRepos(Protocol):
    user: CalendarUserProtocol
    event: CalendarEventProtocol
