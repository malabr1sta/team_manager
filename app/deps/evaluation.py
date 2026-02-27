from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import get_bus, get_session_factory
from app.evaluations import unit_of_work


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def evaluation_uow_factory(
    async_session_factory: SessionFactory,
    event_bus: Bus,
) -> unit_of_work.EvaluationSQLAlchemyUnitOfWork:
    return unit_of_work.EvaluationSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=unit_of_work.EvaluationRepositoryProvider,
    )


async def evaluation_uow(
    uow_factory: Annotated[
        unit_of_work.EvaluationSQLAlchemyUnitOfWork,
        Depends(evaluation_uow_factory),
    ],
) -> AsyncGenerator[
    SQLAlchemyUnitOfWork[unit_of_work.EvaluationRepositoryProvider],
    None,
]:
    async with uow_factory as uow:
        yield uow


EvaluationUoW = Annotated[
    unit_of_work.EvaluationSQLAlchemyUnitOfWork,
    Depends(evaluation_uow),
]
