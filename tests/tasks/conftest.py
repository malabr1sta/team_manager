import pytest
from datetime import datetime, timezone, timedelta

from app.tasks import models as tasks_models, management
from app.core.custom_types import role, ids


@pytest.fixture
def get_team_for_task() -> tuple[
    tasks_models.Team, tasks_models.MemberTask, tasks_models.MemberTask
]:
    manager = tasks_models.MemberTask(
        ids.UserId(2), ids.TeamId(1), role.UserTaskRole.MANAGER
    )
    member = tasks_models.MemberTask(
        ids.UserId(3), ids.TeamId(1), role.UserTaskRole.MEMBER
    )
    return tasks_models.Team(
        ids.TeamId(1), [manager, member]), manager, member


@pytest.fixture
def get_task(get_team_for_task) -> tuple[
    tasks_models.Task,
    tasks_models.Team,
    tasks_models.MemberTask, tasks_models.MemberTask
]:
    team, manager, member = get_team_for_task
    now_time = datetime.now(timezone.utc)
    deadline = now_time + timedelta(days=3)

    task = management.create_task(
        manager.user_id, team,
        deadline, "title", "description",
    )
    return task, team, manager, member

