from app.core.custom_types import ids
from app.scheduling.models import (
        Meeting, MeetingParticipant, User, Team
)

from abc import ABC, abstractmethod
from datetime import datetime

from app.scheduling import custom_exception


def create_meeting(
        user_id: ids.UserId, team: Team,
        meeting_id: ids.MeetingId,
        start: datetime, end: datetime,
        description: str = ""
) -> Meeting:
    """Create Meeting"""
    if not team.is_manager(user_id):
        raise custom_exception.MeetingsManagerException(
            f"User - {user_id} is not manager this team"
        )
    member = MeetingParticipant(user_id, meeting_id)
    meeting = Meeting(
        organizer_id=user_id, team_id=team._id,
        start=start, end=end, participants=[member],
        id=meeting_id, description=description
    )
    return meeting


class MeetingManagement(ABC):
    """Base class for meeting management."""

    def __init__(
        self,
        user_id: ids.UserId, meeting: Meeting,
    ):
        """Initialize management context."""
        if user_id != meeting._organizer_id:
            raise custom_exception.MeetingsManagerException(
                f"User: {user_id} is not organizer"
            )
        self._user_id = user_id
        self._meeting = meeting

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionAddMeeting(MeetingManagement):
    """Add a new user to the meeting."""

    def execute(
        self, user: User, team: Team
    ) -> MeetingParticipant | None:
        return self._meeting.add_participant(user, team)


class ActionRemoveMeeting(MeetingManagement):
    """Remove an existing member from the meetingg."""

    def execute(self, user_id: ids.UserId) -> MeetingParticipant | None:
        return self._meeting.remove_participant(user_id)

class ActionCancelMeeting(MeetingManagement):
    """Cancel meeting."""

    def execute(self):
        self._meeting.cancel()
