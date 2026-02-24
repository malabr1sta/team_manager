from typing import AsyncGenerator, Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.identity.orm_models import UserORM
from app.identity.user_manager import UserManager
from app.identity.unit_of_work import (
    IdentitySQLAlchemyUnitOfWork,
    IdentityRepositoryProvider
)
from app.core.infrastructure.event import EventBus
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.deps.base import (
    get_session,
    get_session_factory,
    get_bus,
    get_settings
)


settings = get_settings()


SessionFactory = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory)
]
Bus = Annotated[EventBus, Depends(get_bus)]


async def user_uow_factory(
        async_session_factory: SessionFactory,
        event_bus: Bus,
) -> IdentitySQLAlchemyUnitOfWork:
    """Factory for Identity UnitOfWork."""
    return IdentitySQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=IdentityRepositoryProvider,
    )


async def user_uow(
        uow_factory: Annotated[
            IdentitySQLAlchemyUnitOfWork, Depends(user_uow_factory)
        ],
) -> AsyncGenerator[SQLAlchemyUnitOfWork[IdentityRepositoryProvider], None]:
    """Identity UnitOfWork with automatic context."""
    async with uow_factory as uow:
        yield uow


IdentityUoW = Annotated[
    SQLAlchemyUnitOfWork[IdentityRepositoryProvider], Depends(user_uow)
]


async def get_user_db(
        session: Annotated[AsyncSession, Depends(get_session)],
):
    """Provide SQLAlchemy user database for fastapi-users."""
    yield SQLAlchemyUserDatabase(session, UserORM)


async def get_user_manager(
        user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
        bus: Bus,
):
    """Provide UserManager for fastapi-users."""
    yield UserManager(user_db, bus)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret_key,
        lifetime_seconds=3600,
    )


bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[UserORM, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
# current_verified_user = fastapi_users.current_user(active=True, verified=True)

UserDepend = Annotated[UserORM, Depends(current_active_user)]
