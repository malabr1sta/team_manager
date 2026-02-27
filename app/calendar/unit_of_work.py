from app.calendar import repository as repo
from app.core.repositories.descriptor import LazyRepo
from app.core.unit_of_work import AbstractSqlRepositoryProvider, SQLAlchemyUnitOfWork


class CalendarRepositoryProvider(AbstractSqlRepositoryProvider):
    """Provides calendar repositories."""

    user = LazyRepo(repo.SQLAlchemyCalendarUserRepository)
    event = LazyRepo(repo.SQLAlchemyCalendarEventRepository)


class CalendarSQLAlchemyUnitOfWork(SQLAlchemyUnitOfWork[CalendarRepositoryProvider]):
    """Implements calendar unit of work."""

    ...
