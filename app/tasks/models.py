from datetime import datetime, timezone
from dataclasses import dataclass
from app.core.custom_types import ids, role, task_status
from app.core.entity import Entity
from app.teams import models as team_models

from abc import ABC, abstractmethod


class Comment(Entity):

    def __init__(self, author_id: ids.UserId, text: str):
        self.author_id = author_id
        self.text = text
        self.created_at = datetime.now(timezone.utc)


class Task(Entity):

    def __init__(self,
                 task_id: ids.TaskId,
                 supervisor: team_models.Member,
                 title: str,
                 description: str,
                 deadline: datetime
    ):
        self.task_id = task_id
        self.supervisor = supervisor
        self.team_id = supervisor.team_id
        self.title = title
        self.description = description
        self.status = task_status.TaskStatus.OPEN
        self.deadline = deadline
        self.comments: list[Comment] = []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.executor_id = None


