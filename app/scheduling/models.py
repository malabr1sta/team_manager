from app.core.custom_types import ids
from app.core.entity import Entity
from app.core.shared.models.users import BaseUser
from app.scheduling import custom_exception

from dataclasses import dataclass
from datetime import datetime, timezone



@dataclass(frozen=True)
class MemberTeam:
    """Represents a team member with an assigned role."""
    user_id: ids.UserId
    team_id: ids.TeamId
    is_manager: bool = False

class Team(Entity):
    """Team for sheduling's context."""

    def __init__(
            self, id: ids.TeamId,
            members: list[MemberTeam]
    ):
        """Create a team with a unique identifier."""
        self._id = id
        self._members = members

    @property
    def members(self) -> tuple[MemberTeam, ...]:
        """Return team members as an immutable collection."""
        return tuple(self._members)

    def is_member(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team member."""
        return any(
            member.user_id == user_id
            for member in self._members
        )

    def is_manager(self, user_id: ids.UserId) -> bool:
            """Check whether the user is already a team member."""
            return MemberTeam(user_id, self._id, True) in self.members


@dataclass(frozen=True)
class MeetingParticipant:
    """The value object representing a meeting participant"""

    user_id: ids.UserId
    meeting_id: ids.MeetingId | None


class Meeting(Entity):
    """Meeting aggregate representing a scheduled team event."""

    def __init__(
        self,
        organizer_id: ids.UserId, team_id: ids.TeamId,
        start: datetime,
        end: datetime,
        participants: list[MeetingParticipant | None],
        id: ids.MeetingId | None = None,
        description: str = "",
        is_cancelled: bool = False,
    ):
        self._id = id
        self._team_id = team_id
        self._organizer_id = organizer_id
        self._description = description
        self._is_cancelled = is_cancelled
        self._participants = participants
        self._start = start
        self._end = end

    def check_participant(
            self, user_id: ids.UserId,
            team: Team
    ):
        """Check that the participant belongs to the team."""
        if not team.is_member(user_id):
            raise custom_exception.MeetingsMemberException(
                f"User: {user_id} is not part of this team"
            )

    def overlaps(self, other: "Meeting") -> bool:
        """Check whether two active meetings overlap in time."""
        if self._is_cancelled or other._is_cancelled:
            return False
        return not (
            self._end <= other._start
            or self._start >= other._end
        )

    def add_participant(
            self, user: "User", team: Team
    ) -> MeetingParticipant | None:
        """Add a user to the meeting if all domain rules are satisfied."""
        self.check_participant(user.id, team)
        user.check_meeting(self)
        participant = MeetingParticipant(user.id, self._id)
        if participant not in self._participants:
            user._meetings.append(self)
            self._participants.append(participant)
            return participant

    def remove_participant(
            self, user_id: ids.UserId
    ) -> MeetingParticipant | None:
        """Remove participant from meeting."""
        if self._organizer_id == user_id:
            return None

        participant = MeetingParticipant(
            user_id=user_id,
            meeting_id=self._id,
        )

        if participant in self._participants:
            self._participants.remove(participant)
            return participant

        return None

    def cancel(self) -> None:
        """Cancel the meeting if it has not started yet."""
        if self._is_cancelled:
            raise custom_exception.MeetingCancelledError(
                "Meeting already cancelled"
            )
        if self._start <= datetime.now(timezone.utc):
            raise custom_exception.MeetingCancelledError(
                "Cannot cancel past or ongoing meeting"
            )
        self._is_cancelled = True


class User(BaseUser):
    """User aggregate representing a system participant."""
    def __init__(
            self, id: ids.UserId, username: str,
            meetings: list[Meeting] | None = None,
    ):
        self.id = id
        self.username = username
        self._meetings = meetings if meetings is not None else []

    @property
    def meetings(self) -> tuple[Meeting, ...]:
        """Return all meetings assigned to the user."""
        return tuple(self._meetings)

    def get_meetings(
        self,
        team_id: ids.TeamId | None = None,
    ) -> tuple[Meeting, ...]:
        """
        Return user's meetings.
        If team_id is provided, returns only meetings for that team.
        """
        if team_id is None:
            return self.meetings

        return tuple(
            meeting
            for meeting in self._meetings if meeting._team_id == team_id
        )

    def check_meeting(
        self,
        new_meeting: Meeting,
    ) -> None:
        """Ensure the new meeting does not overlap with existing ones."""
        for meeting in self.meetings:
            if meeting.overlaps(new_meeting):
                raise custom_exception.MeetingOverlapError(
                    "New meeting overlaps with an existing meeting"
                )
