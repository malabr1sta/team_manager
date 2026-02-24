from typing import TypeVar, Generic, Type
from abc import ABC

from app.core.shared.events import identity as user_event
from app.core.shared.models.users import BaseUser
from app.core.unit_of_work import SQLAlchemyUnitOfWork
from app.core.infrastructure.event import EventHandler
from app.core.custom_types import ids


TUow = TypeVar('TUow', bound=SQLAlchemyUnitOfWork)
TUserDomain = TypeVar('TUserDomain', bound=Type[BaseUser])


class UserCreatedHandler(
    Generic[TUow, TUserDomain],
    ABC
):
    """Handler for UserCreated event."""

    def __init__(
            self,
            uow: TUow,
            domain: TUserDomain
    ):
        self.uow = uow
        self.domain = domain


    async def handle(self, event: user_event.UserRegistered) -> None:
        """Create User."""
        async with self.uow as uow:
            user = self.domain(
                id=ids.UserId(event.user_id),
                username=event.username
            )
            await uow.repos.user.save(user)
            await uow.commit()
