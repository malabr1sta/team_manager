from typing import Type

from app.teams.models import User
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork
)
from app.core.shared.handlers.users import UserCreatedHandler


class TeamUserCreatedHandler(
    UserCreatedHandler[TeamSQLAlchemyUnitOfWork, Type[User]]
):
    ...


