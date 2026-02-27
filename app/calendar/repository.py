from datetime import datetime

from sqlalchemy import select

from app.calendar import mappers, models, orm_models
from app.core.custom_types import calendar_type
from app.core.repositories.base import AbstractRepository


class SQLAlchemyCalendarUserRepository(AbstractRepository[models.CalendarUser]):
    """Persists calendar users."""

    async def get_by_id(self, id: int) -> models.CalendarUser | None:
        result = await self.session.execute(
            select(orm_models.CalendarUserOrm).where(orm_models.CalendarUserOrm.id == id)
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            return None
        return mappers.CalendarUserMapper.to_domain(user_orm)

    async def save(self, domain: models.CalendarUser) -> None:
        result = await self.session.execute(
            select(orm_models.CalendarUserOrm).where(
                orm_models.CalendarUserOrm.id == domain.id
            )
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            self.session.add(mappers.CalendarUserMapper.to_orm(domain))
            return
        mappers.CalendarUserMapper.update_orm(user_orm, domain)


class SQLAlchemyCalendarEventRepository(AbstractRepository[models.CalendarEvent]):
    """Persists calendar events."""

    async def save(self, domain: models.CalendarEvent) -> None:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.user_id == domain.user_id,
                orm_models.CalendarEventOrm.event_type == domain.type,
                orm_models.CalendarEventOrm.reference_id == domain.reference_id,
            )
        )
        event_orm = result.scalar_one_or_none()
        if event_orm is None:
            self.session.add(mappers.CalendarEventMapper.to_orm(domain))
            return
        mappers.CalendarEventMapper.update_orm(event_orm, domain)

    async def get_by_user(self, user_id: int) -> list[models.CalendarEvent]:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.user_id == user_id
            )
        )
        events_orm = result.scalars().all()
        return [mappers.CalendarEventMapper.to_domain(item) for item in events_orm]

    async def get_by_user_and_reference(
            self,
            user_id: int,
            event_type: calendar_type.CalendarEventType,
            reference_id: int,
    ) -> models.CalendarEvent | None:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.user_id == user_id,
                orm_models.CalendarEventOrm.event_type == event_type,
                orm_models.CalendarEventOrm.reference_id == reference_id,
            )
        )
        event_orm = result.scalar_one_or_none()
        if event_orm is None:
            return None
        return mappers.CalendarEventMapper.to_domain(event_orm)

    async def get_by_reference(
            self,
            event_type: calendar_type.CalendarEventType,
            reference_id: int,
    ) -> list[models.CalendarEvent]:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.event_type == event_type,
                orm_models.CalendarEventOrm.reference_id == reference_id,
            )
        )
        events_orm = result.scalars().all()
        return [mappers.CalendarEventMapper.to_domain(item) for item in events_orm]

    async def get_by_user_for_day(
            self,
            user_id: int,
            day_start: datetime,
            day_end: datetime,
    ) -> list[models.CalendarEvent]:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.user_id == user_id,
                orm_models.CalendarEventOrm.time >= day_start,
                orm_models.CalendarEventOrm.time < day_end,
            )
        )
        events_orm = result.scalars().all()
        return [mappers.CalendarEventMapper.to_domain(item) for item in events_orm]

    async def get_by_user_for_month(
            self,
            user_id: int,
            month_start: datetime,
            month_end: datetime,
    ) -> list[models.CalendarEvent]:
        result = await self.session.execute(
            select(orm_models.CalendarEventOrm).where(
                orm_models.CalendarEventOrm.user_id == user_id,
                orm_models.CalendarEventOrm.time >= month_start,
                orm_models.CalendarEventOrm.time < month_end,
            )
        )
        events_orm = result.scalars().all()
        return [mappers.CalendarEventMapper.to_domain(item) for item in events_orm]
