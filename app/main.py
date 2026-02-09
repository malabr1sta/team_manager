from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.deps import base as base_deps
from app.core.infrastructure import event_bus
from app.core.shared.events import teams as teams_event
from app.tasks import (
    handlers as task_handlers,
    repository as task_repo
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
    await app.state.bus.subscribe(
        teams_event.TeamCreated,
        task_handlers.TeamCreatedHandler(
            task_repo.SQLAlchemyTeamRepository,
            app.state.async_session
        )
    )

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
