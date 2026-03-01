"""Authentication backend for sqladmin."""

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.identity.orm_models import UserORM


class AdminAuthBackend(AuthenticationBackend):
    """Provides session auth for admin panel."""

    def __init__(
            self,
            secret_key: str,
            session_factory: async_sessionmaker[AsyncSession],
    ):
        super().__init__(secret_key=secret_key)
        self._password_hasher = PasswordHash.recommended()
        self._session_factory = session_factory

    async def login(self, request: Request) -> bool:
        """Logs in superuser by email and password."""
        form = await request.form()
        email = str(form.get("username", "")).strip().lower()
        password = str(form.get("password", ""))
        if not email or not password:
            return False

        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).filter_by(email=email)
            )
            user = result.scalar_one_or_none()

        if user is None or not user.is_superuser or user.deleted:
            return False

        if not self._password_hasher.verify(password, user.hashed_password):
            return False

        request.session.update(
            {
                "admin_user_id": int(user.id),
                "admin_email": user.email,
            }
        )
        return True

    async def logout(self, request: Request) -> bool:
        """Clears admin session."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Validates existing admin session."""
        admin_user_id = request.session.get("admin_user_id")
        if not admin_user_id:
            return False

        async with self._session_factory() as session:
            result = await session.execute(
                select(UserORM).filter_by(id=int(admin_user_id))
            )
            user = result.scalar_one_or_none()

        return bool(user and user.is_superuser and not user.deleted)
