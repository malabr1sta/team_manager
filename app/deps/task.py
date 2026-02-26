from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import get_bus, get_session_factory
from app.tasks.unit_of_work import TaskRepositoryProvider, TaskSQLAlchemyUnitOfWork


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def task_uow_factory(
    async_session_factory: SessionFactory,
    event_bus: Bus,
) -> TaskSQLAlchemyUnitOfWork:
    return TaskSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TaskRepositoryProvider,
    )


async def task_uow(
    uow_factory: Annotated[TaskSQLAlchemyUnitOfWork, Depends(task_uow_factory)],
) -> AsyncGenerator[SQLAlchemyUnitOfWork[TaskRepositoryProvider], None]:
    async with uow_factory as uow:
        yield uow


TaskUoW = Annotated[TaskSQLAlchemyUnitOfWork, Depends(task_uow)]
