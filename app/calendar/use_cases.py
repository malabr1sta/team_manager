from datetime import date, datetime, time, timedelta, timezone

from fastapi import HTTPException

from app.calendar import dto, models
from app.calendar.unit_of_work import CalendarSQLAlchemyUnitOfWork
from app.core.custom_types import ids


def _to_event_dto(event: models.CalendarEvent) -> dto.CalendarEventReadDTO:
    return dto.CalendarEventReadDTO(
        id=event.id,
        user_id=event.user_id,
        event_type=event.type.value,
        title=event.title,
        description=event.description,
        time=event.time,
        reference_id=event.reference_id,
        cancelled=event.cancelled,
    )


class CalendarEventsForDayUseCase:
    """Reads calendar events for one day."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, user_id: int, day: date) -> dto.CalendarEventsDTO:
        day_start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        events = await self.uow.repos.event.get_by_user_for_day(
            user_id=user_id,
            day_start=day_start,
            day_end=day_end,
        )
        calendar = models.Calendar(
            user_id=ids.UserId(user_id),
            calendar_events=events,
        )
        items = [_to_event_dto(event) for event in calendar.events_for_day(day_start)]
        return dto.CalendarEventsDTO(items=items, total=len(items))


class CalendarEventsForMonthUseCase:
    """Reads calendar events for one month."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
            self,
            user_id: int,
            year: int,
            month: int,
    ) -> dto.CalendarEventsDTO:
        if month < 1 or month > 12:
            raise HTTPException(400, "Month must be in range 1..12")
        month_start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            month_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            month_end = datetime(year, month + 1, 1, tzinfo=timezone.utc)
        events = await self.uow.repos.event.get_by_user_for_month(
            user_id=user_id,
            month_start=month_start,
            month_end=month_end,
        )
        calendar = models.Calendar(
            user_id=ids.UserId(user_id),
            calendar_events=events,
        )
        items = [
            _to_event_dto(event)
            for event in calendar.events_for_month(year=year, month=month)
        ]
        return dto.CalendarEventsDTO(items=items, total=len(items))
