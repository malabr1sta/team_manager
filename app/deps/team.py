from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork,
    TeamRepositoryProvider
)
from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import (
    get_session,
    get_session_factory,
    get_bus,
    get_settings
)


settings = get_settings()


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def team_uow_factory(
        async_session_factory: SessionFactory,
        event_bus: Bus,
) -> TeamSQLAlchemyUnitOfWork:
    """Factory for Team UnitOfWork."""
    return TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider,
    )


async def team_uow(
        uow_factory: Annotated[
            TeamSQLAlchemyUnitOfWork, Depends(team_uow_factory)
        ],
) -> AsyncGenerator[SQLAlchemyUnitOfWork[TeamRepositoryProvider], None]:
    """Identity UnitOfWork with automatic context."""
    async with uow_factory as uow:
        yield uow


TeamUoW = Annotated[
    TeamSQLAlchemyUnitOfWork, Depends(team_uow)
]
