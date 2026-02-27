from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.calendar.unit_of_work import CalendarRepositoryProvider, CalendarSQLAlchemyUnitOfWork
from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import get_bus, get_session_factory


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def calendar_uow_factory(
    async_session_factory: SessionFactory,
    event_bus: Bus,
) -> CalendarSQLAlchemyUnitOfWork:
    return CalendarSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=CalendarRepositoryProvider,
    )


async def calendar_uow(
    uow_factory: Annotated[CalendarSQLAlchemyUnitOfWork, Depends(calendar_uow_factory)],
) -> AsyncGenerator[
    SQLAlchemyUnitOfWork[CalendarRepositoryProvider],
    None,
]:
    async with uow_factory as uow:
        yield uow


CalendarUoW = Annotated[CalendarSQLAlchemyUnitOfWork, Depends(calendar_uow)]
