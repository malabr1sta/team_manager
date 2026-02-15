import pytest
from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
)
from app.core.database import Base
from app.core.infrastructure.event_bus import MemoryEventBus
from app.core.register_handlers import register_event_handlers


@pytest.fixture(scope="function")
async def engine():
    """Create the engine and session once for all tests."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def async_session_factory(engine):
    """Create session factory for tests."""
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="function")
def event_bus():
    """Create event bus for tests."""
    bus = MemoryEventBus()
    yield bus
    bus._handlers.clear()


@pytest.fixture
async def async_session(engine):
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
