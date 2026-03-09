from typing import Protocol, runtime_checkable

from app.core.repositories.scheduling import SchedulingRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class SchedulingUnitOfWork(Protocol):
    @property
    def repos(self) -> SchedulingRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class SchedulingHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> SchedulingRepos: ...
