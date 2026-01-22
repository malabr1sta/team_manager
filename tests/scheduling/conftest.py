import pytest
from datetime import datetime, timedelta, timezone

from app.core.custom_types import ids
from app.scheduling.models import Team, MemberTeam, User, Meeting

@pytest.fixture
def team():
    return Team(
        id=ids.TeamId(1),
        members=[MemberTeam(user_id=ids.UserId(1), team_id=ids.TeamId(1))]
    )

@pytest.fixture
def user():
    return User(
        id=ids.UserId(1),
        username="alice",
        meetings=[]
    )

@pytest.fixture
def meeting(team):
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)
    return Meeting(
        id=ids.MeetingId(1),
        organizer_id=ids.UserId(111),
        team_id=team._id,
        start=start,
        end=end,
        participants=[]
    )

@pytest.fixture
def overlapping_meeting(team, meeting):
    start = meeting._start + timedelta(minutes=30)
    end = meeting._end + timedelta(hours=1)
    return Meeting(
        id=ids.MeetingId(1),
        organizer_id=ids.UserId(222),
        team_id=team._id,
        start=start,
        end=end,
        participants=[]
    )

@pytest.fixture
def non_overlapping_meeting(team, meeting):
    start = meeting._end + timedelta(minutes=10)
    end = start + timedelta(hours=1)
    return Meeting(
        id=ids.MeetingId(1),
        organizer_id=ids.UserId(333),
        team_id=team._id,
        start=start,
        end=end,
        participants=[]
    )
