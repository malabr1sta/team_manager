from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import AsyncGenerator
from fastapi import Request


from app.core import config
from app.core.infrastructure import event


@lru_cache
def get_settings():
    return config.Settings()


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.async_session() as session:
        yield session


async def get_session_factory(
        request: Request
) -> async_sessionmaker[AsyncSession]:
    return request.app.state.async_session


async def get_bus(request: Request) -> event.EventBus:
    return request.app.state.bus
