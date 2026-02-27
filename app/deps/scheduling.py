from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import get_bus, get_session_factory
from app.scheduling.unit_of_work import (
    SchedulingRepositoryProvider,
    SchedulingSQLAlchemyUnitOfWork,
)


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def scheduling_uow_factory(
    async_session_factory: SessionFactory,
    event_bus: Bus,
) -> SchedulingSQLAlchemyUnitOfWork:
    return SchedulingSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=SchedulingRepositoryProvider,
    )


async def scheduling_uow(
    uow_factory: Annotated[
        SchedulingSQLAlchemyUnitOfWork, Depends(scheduling_uow_factory)
    ],
) -> AsyncGenerator[
    SQLAlchemyUnitOfWork[SchedulingRepositoryProvider], None
]:
    async with uow_factory as uow:
        yield uow


SchedulingUoW = Annotated[SchedulingSQLAlchemyUnitOfWork, Depends(scheduling_uow)]
