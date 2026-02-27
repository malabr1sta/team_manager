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


class UserUpdatedHandler(
    Generic[TUow, TUserDomain],
    ABC
):
    """Handler for UserUpdated event."""

    def __init__(
            self,
            uow: TUow,
            domain: TUserDomain
    ):
        self.uow = uow
        self.domain = domain

    async def handle(self, event: user_event.UserUpdated) -> None:
        """Update projected user."""
        async with self.uow as uow:
            user = self.domain(
                id=ids.UserId(event.user_id),
                username=event.username
            )
            await uow.repos.user.save(user)
            await uow.commit()


class UserDeletedHandler(
    Generic[TUow, TUserDomain],
    ABC
):
    """Handler for UserDeleted event."""

    def __init__(
            self,
            uow: TUow,
            domain: TUserDomain
    ):
        self.uow = uow
        self.domain = domain

    async def handle(self, event: user_event.UserDeleted) -> None:
        """
        Mark projected user as deleted without removing row.

        We keep projection rows to preserve FK integrity
        in cross-context tables.
        """
        async with self.uow as uow:
            deleted_user = self.domain(
                id=ids.UserId(event.user_id),
                username="deleted_user",
            )
            await uow.repos.user.save(deleted_user)
            await uow.commit()
