from app.core.custom_types import ids
from app.scheduling.models import (
        Meeting, User, Team
)

from abc import ABC, abstractmethod



class MeetingManagement(ABC):
    """Base class for meeting management."""

    def __init__(
        self,
        user: User, team: Team
    ):
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

