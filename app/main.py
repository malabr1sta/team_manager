from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.deps import base as base_deps
from app.core.infrastructure import event_bus
from app.core.register_handlers import register_event_handlers


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

    await register_event_handlers(
        app.state.bus,
        app.state.async_session
    )

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
