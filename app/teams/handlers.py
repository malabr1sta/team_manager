from typing import Type

from app.teams.models import User
from app.core.uow.teams import TeamHandlerUnitOfWork
from app.core.shared.handlers.users import (
    UserCreatedHandler,
    UserDeletedHandler,
    UserUpdatedHandler,
)


class TeamUserCreatedHandler(
    UserCreatedHandler[TeamHandlerUnitOfWork, Type[User]]
):
    ...


class TeamUserUpdatedHandler(
    UserUpdatedHandler[TeamHandlerUnitOfWork, Type[User]]
):
    ...


class TeamUserDeletedHandler(
    UserDeletedHandler[TeamHandlerUnitOfWork, Type[User]]
):
    ...

