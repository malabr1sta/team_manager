from dataclasses import dataclass

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class TaskCreated(DomainEvent):
    task_id: int
    team_id: int
    supervisor_id: int
    executor_id: int | None
    status: str


@dataclass(frozen=True)
class TaskUpdated(DomainEvent):
    task_id: int
    team_id: int
    supervisor_id: int
    executor_id: int | None
    status: str
