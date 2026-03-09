from typing import Protocol, runtime_checkable

from app.core.repositories.evaluations import EvaluationRepos
from app.core.uow.handlers import HandlerUnitOfWork


@runtime_checkable
class EvaluationUnitOfWork(Protocol):
    @property
    def repos(self) -> EvaluationRepos: ...

    async def commit(self) -> None: ...


@runtime_checkable
class EvaluationHandlerUnitOfWork(HandlerUnitOfWork, Protocol):
    @property
    def repos(self) -> EvaluationRepos: ...
