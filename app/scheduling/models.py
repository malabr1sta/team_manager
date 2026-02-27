from app.core.custom_types import ids
from app.core.aggregate import AggregateRoot
from app.core.entity import Entity
from app.core.shared.events import meetings as meeting_event
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
    def id(self) -> ids.TeamId:
        return self._id

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

    def add_member(
            self,
            user_id: ids.UserId,
            is_manager: bool,
    ) -> MemberTeam | None:
        new_member = MemberTeam(
            user_id=user_id,
            team_id=self._id,
            is_manager=is_manager,
        )
        if new_member in self._members:
            return None
        self._members = [item for item in self._members if item.user_id != user_id]
        self._members.append(new_member)
        return new_member

    def remove_member(self, user_id: ids.UserId) -> MemberTeam | None:
        for member in self._members:
            if member.user_id == user_id:
                self._members.remove(member)
                return member
        return None

    def change_member_role(
            self,
            user_id: ids.UserId,
            is_manager: bool,
    ) -> MemberTeam | None:
        for index, member in enumerate(self._members):
            if member.user_id == user_id:
                updated_member = MemberTeam(
                    user_id=user_id,
                    team_id=self._id,
                    is_manager=is_manager,
                )
                self._members[index] = updated_member
                return updated_member
        return None


@dataclass(frozen=True)
class MeetingParticipant:
    """The value object representing a meeting participant"""

    user_id: ids.UserId
    meeting_id: ids.MeetingId | None


class Meeting(Entity, AggregateRoot):
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
        AggregateRoot.__init__(self)
        self._id = id
        self._team_id = team_id
        self._organizer_id = organizer_id
        self._description = description
        self._is_cancelled = is_cancelled
        self._participants = participants
        self._start = start
        self._end = end

    def _participant_ids(self) -> list[int]:
        return [
            int(participant.user_id)
            for participant in self._participants
            if participant is not None
        ]

    def mark_created_event(self) -> None:
        if self._id is None:
            return
        self.record_event(
            meeting_event.MeetingCreated(
                meeting_id=int(self._id),
                team_id=int(self._team_id),
                organizer_id=int(self._organizer_id),
                participant_ids=self._participant_ids(),
                start=self._start,
                end=self._end,
                description=self._description,
                is_cancelled=self._is_cancelled,
            )
        )

    def mark_updated_event(self, previous_participant_ids: list[int]) -> None:
        if self._id is None:
            return
        self.record_event(
            meeting_event.MeetingUpdated(
                meeting_id=int(self._id),
                team_id=int(self._team_id),
                organizer_id=int(self._organizer_id),
                participant_ids=self._participant_ids(),
                previous_participant_ids=previous_participant_ids,
                start=self._start,
                end=self._end,
                description=self._description,
                is_cancelled=self._is_cancelled,
            )
        )

    def mark_cancelled_event(self) -> None:
        if self._id is None:
            return
        self.record_event(
            meeting_event.MeetingCancelled(
                meeting_id=int(self._id),
                team_id=int(self._team_id),
                organizer_id=int(self._organizer_id),
                participant_ids=self._participant_ids(),
            )
        )

    @property
    def id(self) -> ids.MeetingId | None:
        return self._id

    @property
    def team_id(self) -> ids.TeamId:
        return self._team_id

    @property
    def organizer_id(self) -> ids.UserId:
        return self._organizer_id

    @property
    def description(self) -> str:
        return self._description

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    @property
    def participants(self) -> tuple[MeetingParticipant | None, ...]:
        return tuple(self._participants)

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def end(self) -> datetime:
        return self._end

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
        start = self._start
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if start <= datetime.now(timezone.utc):
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
