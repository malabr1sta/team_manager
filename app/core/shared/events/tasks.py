from dataclasses import dataclass
from datetime import datetime

from app.core.infrastructure.event import DomainEvent


@dataclass(frozen=True)
class TaskCreated(DomainEvent):
    task_id: int
    team_id: int
    supervisor_id: int
    executor_id: int | None
    status: str
    title: str = ""
    description: str = ""
    deadline: datetime | None = None
    deleted: bool = False


@dataclass(frozen=True)
class TaskUpdated(DomainEvent):
    task_id: int
    team_id: int
    supervisor_id: int
    executor_id: int | None
    status: str
    previous_executor_id: int | None = None
    title: str = ""
    description: str = ""
    deadline: datetime | None = None
    deleted: bool = False
