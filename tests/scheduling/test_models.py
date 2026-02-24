import pytest
from datetime import datetime, timedelta, timezone

from app.core.custom_types import ids
from app.scheduling import custom_exception
from app.scheduling.models import (
    Team, Meeting, MemberTeam
)
from app.scheduling.management import (
    create_meeting,
    ActionAddMeeting,
    ActionCancelMeeting,
    ActionRemoveMeeting,
)


class TestMeeting:
    def test_check_meeting_no_overlap(
            self, user, meeting, non_overlapping_meeting
    ):
        user._meetings.append(meeting)
        user.check_meeting(non_overlapping_meeting)

    def test_check_meeting_overlap_raises(
            self, user, meeting, overlapping_meeting
    ):
        user._meetings.append(meeting)
        with pytest.raises(custom_exception.MeetingOverlapError):
            user.check_meeting(overlapping_meeting)

    def test_add_participant_success(self, user, team, meeting):
        meeting.add_participant(user, team)
        assert meeting in user._meetings
        assert any(p.user_id == user.id for p in meeting._participants)

    def test_add_participant_not_team_member(self, user):
        other_team = Team(
            id=ids.TeamId(2),
            members=[]
        )
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)
        meeting = Meeting(
            organizer_id=1,
            team_id=other_team._id,
            start=start,
            end=end,
            participants=[]
        )
        with pytest.raises(custom_exception.MeetingsMemberException):
            meeting.add_participant(user, other_team)


    def test_cancel_meeting_success(self, team):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)
        meeting = Meeting(
            organizer_id=ids.UserId(111),
            team_id=team._id,
            start=start,
            end=end,
            participants=[]
        )
        meeting.cancel()
        assert meeting._is_cancelled

    def test_cancel_meeting_already_cancelled(self, team):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)
        meeting = Meeting(
            organizer_id=ids.UserId(1),
            team_id=team._id,
            start=start,
            end=end,
            participants=[],
            is_cancelled=True
        )
        with pytest.raises(custom_exception.MeetingCancelledError):
            meeting.cancel()

    def test_cancel_meeting_in_past(self, team):
        start = datetime.now(timezone.utc) - timedelta(hours=2)
        end = datetime.now(timezone.utc) - timedelta(hours=1)
        meeting = Meeting(
            organizer_id=ids.UserId(1),
            team_id=team._id,
            start=start,
            end=end,
            participants=[]
        )
        with pytest.raises(custom_exception.MeetingCancelledError):
            meeting.cancel()


class TestMeetingManagement:

    def test_create_meeting_success(self):
        manager_id = ids.UserId(1)
        meeting_id = ids.MeetingId(1)

        team = Team(
            id=ids.TeamId(1),
            members=[
                MemberTeam(
                    user_id=manager_id,
                    team_id=ids.TeamId(1),
                    is_manager=True,
                )
            ],
        )

        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)

        meeting = create_meeting(
            user_id=manager_id,
            team=team,
            meeting_id=meeting_id,
            start=start,
            end=end,
            description="Daily standup",
        )

        assert meeting._organizer_id == manager_id
        assert meeting._id == meeting_id
        assert len(meeting._participants) == 1
        participant = meeting._participants[0]
        assert participant
        assert participant.user_id == manager_id

    def test_create_meeting_not_manager_raises(self):
        user_id = ids.UserId(2)
        meeting_id = ids.MeetingId(1)

        team = Team(
            id=ids.TeamId(1),
            members=[
                MemberTeam(
                    user_id=ids.UserId(1),
                    team_id=ids.TeamId(1),
                    is_manager=True,
                )
            ],
        )

        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=1)

        with pytest.raises(custom_exception.MeetingsManagerException):
            create_meeting(
                user_id=user_id,
                team=team,
                meeting_id=meeting_id,
                start=start,
                end=end,
            )

    def test_meeting_management_not_organizer_raises(self, meeting):
        with pytest.raises(custom_exception.MeetingsManagerException):
            ActionCancelMeeting(
                user_id=ids.UserId(999),
                meeting=meeting,
            )

    def test_action_add_meeting_success(self, user, team, meeting):
        action = ActionAddMeeting(
            user_id=meeting._organizer_id,
            meeting=meeting,
        )

        participant = action.execute(
            user=user,
            team=team,
        )

        assert participant is not None
        assert participant.user_id == user.id
        assert meeting in user._meetings

    def test_action_remove_meeting_success(self, user, team, meeting):
        meeting.add_participant(user, team)

        action = ActionRemoveMeeting(
            user_id=meeting._organizer_id,
            meeting=meeting,
        )

        removed = action.execute(
            user_id=user.id,
        )

        assert removed
        assert removed.user_id == user.id
        assert all(
            participant.user_id != user.id
            for participant in meeting._participants
        )

    def test_action_cancel_meeting_success(self, meeting):

        action = ActionCancelMeeting(
            user_id=meeting._organizer_id,
            meeting=meeting,
        )
        action.execute()
        assert meeting._is_cancelled

    def test_action_cancel_meeting_not_organizer_raises(self, team):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=2)

        meeting = Meeting(
            organizer_id=ids.UserId(1),
            team_id=team._id,
            start=start,
            end=end,
            participants=[],
        )

        with pytest.raises(custom_exception.MeetingsManagerException):
            ActionCancelMeeting(
                user_id=ids.UserId(999),
                meeting=meeting,
            )
