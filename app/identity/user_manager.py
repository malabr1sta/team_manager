from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.core.infrastructure.event import EventBus
from app.core.shared.events import identity as identity_event
from app.deps.base import get_settings
from app.identity.orm_models import UserORM


settings = get_settings()


class UserManager(IntegerIDMixin, BaseUserManager[UserORM, int]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    def __init__(self, user_db, bus: EventBus):
        super().__init__(user_db)
        self._bus = bus

    async def on_after_register(
        self, user: UserORM, request: Request | None = None
    ) -> None:
        await self._bus.publish(
            identity_event.UserRegistered(
                user_id=user.id,
                username=user.username,
            )
        )
        # await self.request_verify(user, request)
