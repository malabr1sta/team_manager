from typing import Type

from app.teams.models import User
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork
)
from app.core.shared.handlers.users import (
    UserCreatedHandler,
    UserDeletedHandler,
    UserUpdatedHandler,
)


class TeamUserCreatedHandler(
    UserCreatedHandler[TeamSQLAlchemyUnitOfWork, Type[User]]
):
    ...


class TeamUserUpdatedHandler(
    UserUpdatedHandler[TeamSQLAlchemyUnitOfWork, Type[User]]
):
    ...


class TeamUserDeletedHandler(
    UserDeletedHandler[TeamSQLAlchemyUnitOfWork, Type[User]]
):
    ...


