from typing import TYPE_CHECKING

from app.calendar import repository as repo
from app.core.repositories.calendar import (
    CalendarUserProtocol,
    CalendarEventProtocol,
)
from app.core.repositories.descriptor import LazyRepo
from app.core.unit_of_work import (
    AbstractSqlRepositoryProvider,
    SQLAlchemyUnitOfWork,
)


class CalendarRepositoryProvider(AbstractSqlRepositoryProvider):
    """Provides calendar repositories."""
    if TYPE_CHECKING:
        user: CalendarUserProtocol
        event: CalendarEventProtocol
    else:
        user = LazyRepo(repo.SQLAlchemyCalendarUserRepository)
        event = LazyRepo(repo.SQLAlchemyCalendarEventRepository)


class CalendarSQLAlchemyUnitOfWork(
    SQLAlchemyUnitOfWork[CalendarRepositoryProvider]
):
    ...
