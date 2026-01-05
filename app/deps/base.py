from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from fastapi import Depends, Request
from fastapi_users.db import SQLAlchemyUserDatabase

from typing import Annotated

from app.core import config
from app.domain.users import model as user_model


@lru_cache
def get_settings():
    return config.Settings()


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.async_session() as session:
        yield session


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield SQLAlchemyUserDatabase(session, user_model.User)
