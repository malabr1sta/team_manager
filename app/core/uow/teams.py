from typing import Protocol, runtime_checkable

from app.core.repositories.teams import TeamRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class TeamUnitOfWork(Protocol):
    @property
    def repos(self) -> TeamRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class TeamHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> TeamRepos: ...
