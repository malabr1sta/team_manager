import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
)
from fastapi import FastAPI, status
from httpx import AsyncClient, ASGITransport

from app.core.database import Base
from app.core.infrastructure.event_bus import MemoryEventBus
from app.core.register_handlers import register_event_handlers
from app.routers import (
    evaluations as evaluations_router,
    identity as identity_router,
    teams as teams_roter,
    tasks as tasks_router,
)



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


@pytest.fixture(scope="function")
async def test_app():
    """Create FastAPI app with initialized state."""

    app = FastAPI()

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                text("PRAGMA foreign_keys = ON")
            )
        )
        await conn.run_sync(Base.metadata.create_all)

    app.state.async_session = async_sessionmaker(
        engine, expire_on_commit=False
    )
    app.state.bus = MemoryEventBus()
    await register_event_handlers(app.state.bus, app.state.async_session)

    PREFIX = "/api/v1"
    app.include_router(identity_router.auth_router, prefix=PREFIX)
    app.include_router(identity_router.users_router, prefix=PREFIX)
    app.include_router(teams_roter.teams_router, prefix=PREFIX)
    app.include_router(tasks_router.tasks_router, prefix=PREFIX)
    app.include_router(evaluations_router.evaluations_router, prefix=PREFIX)

    yield app
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_app):
    """HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def registered_user(client):
    """Register user and return credentials."""
    credentials = {
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "username": "testuser"
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=credentials
    )
    assert response.status_code == status.HTTP_201_CREATED

    return {
        **credentials,
        "id": response.json()["id"]
    }


@pytest.fixture
async def auth_token(client, registered_user):
    """Get authentication token for registered user."""
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    return response.json()["access_token"]


@pytest.fixture
async def authenticated_client(client, auth_token):
    """HTTP client with authentication header."""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client
