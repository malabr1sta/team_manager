from typing import Protocol, runtime_checkable

from app.core.repositories.identity import IdentityRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class IdentityUnitOfWork(Protocol):
    @property
    def repos(self) -> IdentityRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class IdentityHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> IdentityRepos: ...
