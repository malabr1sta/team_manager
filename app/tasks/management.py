from datetime import datetime, timezone
from app.core.custom_types import ids, role, task_patch
from app.tasks import custom_exception
from app.tasks.models import Comment, Task, Team

from abc import ABC, abstractmethod
from typing import Unpack


def create_task(
        user_id: ids.UserId,
        team: Team,
        deadline: datetime,
        title: str,
        description: str,
) -> Task:
    """Create a new task supervised by a manager;
    deadline must be in the future."""

    if not team.has_member(user_id, role.UserTaskRole.MANAGER):
        raise custom_exception.TaskSupervisorException(
            "Member is not at task supervisor"
        )

    now_time = datetime.now(timezone.utc)

    if deadline < now_time:
        raise custom_exception.TaskDeadlineException(
            "The deadline can't be in the past."
        )

    task = Task(
        supervisor_id=user_id,
        team_id=team.id,
        title=title,
        description=description,
        deadline=deadline,
        created_at=now_time,
        updated_at=now_time
    )

    return task


class TaskManagement(ABC):
    """Base class for task management."""

    def __init__(self, task: Task, user_id: ids.UserId):
        """Initialize management context."""
        if task.supervisor_id != user_id:
            raise custom_exception.TaskSupervisorException(
                "Member is not at task supervisor"
            )
        self._task = task

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionAppointmentExecutorTask(TaskManagement):
    """Assigns an executor to the task."""

    def execute(self, user_id: ids.UserId, team: Team):
        """Validates the member and sets them as the task executor."""
        self._task.set_executor(user_id, team)


class ActionUpdateTask(TaskManagement):
    """Update fields to the task"""

    def execute(self, **args: Unpack[task_patch.TaskUpdateArgs]):
        self._task.update_task(**args)


class CommentManagement(ABC):
    """Base class for comment management."""

    def __init__(self, team: Team, author_id: ids.UserId):
        """Initialize management context."""
        if not team.is_member(author_id):
            raise custom_exception.CommentException(
                "Team has not this user"
            )
        self._team = team
        self._author_id = author_id

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionCreateComment(CommentManagement):
    """Class create new comment"""

    def execute(
            self, task_id: ids.TaskId, text: str,
            comment_id: ids.CommentId
    ) -> Comment:
        comment = Comment(
            self._author_id, task_id, text,
            self._team.id,
            comment_id, datetime.now(timezone.utc)
        )
        return comment
