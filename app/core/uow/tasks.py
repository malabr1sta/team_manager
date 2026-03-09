from typing import Protocol, runtime_checkable

from app.core.repositories.tasks import TaskRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class TaskUnitOfWork(Protocol):
    @property
    def repos(self) -> TaskRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class TaskHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> TaskRepos: ...
