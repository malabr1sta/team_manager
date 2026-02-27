from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.deps import base as base_deps
from app.core.infrastructure import event_bus
from app.core.register_handlers import register_event_handlers
from app.routers import (
    evaluations as evaluations_router,
    identity as identity_router,
    teams as teams_roter,
    tasks as tasks_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = base_deps.get_settings()

    engine = create_async_engine(
        f"postgresql+asyncpg://{settings.database_user}:"
        f"{settings.database_password}@"
        f"{settings.database_host}:{settings.database_port}/"
        f"{settings.database_name}",
        echo=True
    )

    app.state.async_session = async_sessionmaker(
        engine, expire_on_commit=False
    )
    app.state.bus = event_bus.MemoryEventBus()

    await register_event_handlers(app.state.bus, app.state.async_session)

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


PREFIX = "/api/v1"

app.include_router(identity_router.auth_router, prefix=PREFIX)
app.include_router(identity_router.users_router, prefix=PREFIX)
app.include_router(teams_roter.teams_router, prefix=PREFIX)
app.include_router(tasks_router.tasks_router, prefix=PREFIX)
app.include_router(evaluations_router.evaluations_router, prefix=PREFIX)
