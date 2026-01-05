from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from typing import Annotated

from app.domain.users import model as user_model
from app.deps import base as base_deps


async def get_user_db(
    session: Annotated[AsyncSession, Depends(base_deps.get_session)],
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, user_model.User)

