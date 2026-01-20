import pytest
from datetime import datetime, timedelta, timezone

from app.core.custom_types import ids
from app.scheduling import custom_exception
from app.scheduling.models import Team, Meeting


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
        assert any(p.user_id == user._id for p in meeting._participants)

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
            organizer_id=1,
            team_id=team._id,
            start=start,
            end=end,
            participants=[]
        )
        meeting.cancel()
        assert not meeting._is_cancelled

    def test_cancel_meeting_already_cancelled(self, team):
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=1)
        meeting = Meeting(
            organizer_id=1,
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
            organizer_id=1,
            team_id=team._id,
            start=start,
            end=end,
            participants=[]
        )
        with pytest.raises(custom_exception.MeetingCancelledError):
            meeting.cancel()
