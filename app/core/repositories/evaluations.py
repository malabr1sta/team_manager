from datetime import datetime
from typing import Protocol, runtime_checkable

from app.evaluations.models import Evaluation, Task, User


@runtime_checkable
class EvaluationUserProtocol(Protocol):
    """Protocol user's repository"""

    async def get_by_id(self, id: int) -> User | None:
        ...

    async def save(self, domain: User) -> None:
        ...


@runtime_checkable
class EvaluationTaskProtocol(Protocol):
    """Protocol task's repository"""

    async def get_by_id(self, id: int) -> Task | None:
        ...

    async def save(self, domain: Task) -> None:
        ...


@runtime_checkable
class EvaluationProtocol(Protocol):
    """Protocol evaluation's repository"""

    async def save(self, domain: Evaluation) -> None:
        ...

    async def get_by_user(
        self,
        user_id: int,
        team_id: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[Evaluation]:
        ...


@runtime_checkable
class EvaluationRepos(Protocol):
    user: EvaluationUserProtocol
    task: EvaluationTaskProtocol
    evaluation: EvaluationProtocol
