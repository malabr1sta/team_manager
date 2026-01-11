import pytest
from datetime import datetime, timezone, timedelta

from app.teams import models as teams_models
from app.core.custom_types import role, ids




@pytest.fixture
def get_team_admin() -> tuple[teams_models.Team, teams_models.Member]:
    admin = teams_models.Member(
        ids.UserId(1), ids.TeamId(1), role.UserRole.ADMIN
    )
    return teams_models.Team(ids.TeamId(1), [admin]), admin

@pytest.fixture
def get_team_for_task() -> tuple[
    teams_models.Team, teams_models.Member, teams_models.Member
]:
    admin = teams_models.Member(
        ids.UserId(1), ids.TeamId(1), role.UserRole.ADMIN
    )
    manager = teams_models.Member(
        ids.UserId(2), ids.TeamId(1), role.UserRole.MANAGER
    )
    member = teams_models.Member(
        ids.UserId(3), ids.TeamId(1), role.UserRole.MEMBER
    )
    return teams_models.Team(
        ids.TeamId(1), [admin, manager, member]), manager, member


@pytest.fixture
def new_member() -> teams_models.Member:
    return teams_models.Member(
        ids.UserId(2), ids.TeamId(1), role.UserRole.MEMBER
    )

@pytest.fixture
def get_task(get_team_for_task) -> tuple[
    teams_models.Task,
    teams_models.Team,
    teams_models.Member, teams_models.Member
]:
    team, manager, member = get_team_for_task
    now_time = datetime.now(timezone.utc)
    deadline = now_time + timedelta(days=3)

    task = teams_models.create_task(
        manager.user_id, team,
        deadline, "title", "description",
    )
    return task, team, manager, member




