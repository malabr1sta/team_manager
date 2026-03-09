from typing import Protocol, runtime_checkable

from app.core.repositories.teams import TeamRepos


@runtime_checkable
class TeamUnitOfWork(Protocol):
    @property
    def repos(self) -> TeamRepos: ...

    async def commit(self) -> None: ...
