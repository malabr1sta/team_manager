from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from fastapi import FastAPI

from app import config


@lru_cache
def get_settings():
    return config.Settings()


async def get_session(app: FastAPI) -> AsyncGenerator[AsyncSession, None]:
    async with app.state.async_session() as session:
        yield session
