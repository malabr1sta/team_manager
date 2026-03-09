from types import TracebackType
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HandlerUnitOfWork(Protocol):
    @property
    def repos(self) -> Any: ...

    async def commit(self) -> None: ...

    async def __aenter__(self) -> "HandlerUnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
