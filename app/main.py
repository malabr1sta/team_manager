from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app import dependencies


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = dependencies.get_settings()

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

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
