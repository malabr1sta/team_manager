import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
)
from app.core.infrastructure.event_bus import MemoryEventBus
from app.core.register_handlers import register_event_handlers
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork,
    TeamRepositoryProvider
)
from app.tasks.unit_of_work import (
    TaskSQLAlchemyUnitOfWork,
    TaskRepositoryProvider
)


@pytest.fixture(scope="function")
async def registered_event_bus(
    event_bus: MemoryEventBus,
    async_session_factory: async_sessionmaker[AsyncSession]
):
    """
    Create event bus with all handlers registered.
    This fixture mimics the production register_event_handlers setup.
    """
    await register_event_handlers(event_bus, async_session_factory)
    yield event_bus
    event_bus._handlers.clear()


@pytest.fixture(scope="function")
def teams_uow_factory(async_session_factory, event_bus):
    """Factory for Tasks UnitOfWork."""

    return TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    )


@pytest.fixture
async def teams_uow(
        teams_uow_factory
) -> AsyncGenerator[TeamSQLAlchemyUnitOfWork, None]:
    """Tasks UnitOfWork with automatic context."""
    async with teams_uow_factory as uow:
        yield uow


@pytest.fixture(scope="function")
def tasks_uow_factory(async_session_factory, event_bus):
    """Factory for Tasks UnitOfWork."""

    return TaskSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TaskRepositoryProvider
    )


@pytest.fixture
async def tasks_uow(tasks_uow_factory):
    """Tasks UnitOfWork with automatic context."""
    async with tasks_uow_factory as uow:
        yield uow
