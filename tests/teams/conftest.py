import pytest
from app.teams import models as teams_models
from app.core.custom_types import role, ids


@pytest.fixture
def get_team_admin() -> tuple[teams_models.Team, teams_models.Member]:
    admin = teams_models.Member(
        ids.UserId(1), ids.TeamId(1), role.UserRole.ADMIN
    )
    return teams_models.Team(ids.TeamId(1), [admin]), admin

@pytest.fixture
def new_member() -> teams_models.Member:
    return teams_models.Member(
        ids.UserId(2), ids.TeamId(1), role.UserRole.MEMBER
    )
