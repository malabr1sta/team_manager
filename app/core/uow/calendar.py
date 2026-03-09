from typing import Protocol, runtime_checkable

from app.core.repositories.calendar import CalendarRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class CalendarUnitOfWork(Protocol):
    @property
    def repos(self) -> CalendarRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class CalendarHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> CalendarRepos: ...
