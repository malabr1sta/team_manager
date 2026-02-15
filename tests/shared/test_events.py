import pytest

from app.core.custom_types import ids
from app.teams import (
    management as teams_management
)
from app.teams.unit_of_work import TeamSQLAlchemyUnitOfWork
from app.tasks.unit_of_work import (
    TaskSQLAlchemyUnitOfWork,
)


@pytest.mark.anyio
async def test_task_team_created_after_team_creation(
    registered_event_bus,
    teams_uow: TeamSQLAlchemyUnitOfWork,
    tasks_uow: TaskSQLAlchemyUnitOfWork
):
    """
    Test that TaskTeam is automatically created when Team is created.

    Flow:
    1. Create Team using domain function
    2. Record TeamCreated event
    3. Save Team via UoW
    4. Commit triggers event publication
    5. TeamCreatedHandler creates TaskTeam
    6. Verify TaskTeam exists with correct data
    """
    # Arrange: Create team with event
    user_id = ids.UserId(1)
    team_name = "Engineering Team"

    team = teams_management.create_team(
        user_id=user_id,
        team_id=None,
        name=team_name
    )
    await teams_uow.repos.team.save(team)
    assert team.id is not None

    teams_management.make_team_created_event(team)

    # Act: Save team (this will trigger TeamCreated event and handler)
    await teams_uow.commit()
    team1 = await teams_uow.repos.team.get_by_id(team.id)
    assert team1 is not None
    assert team1.members is not None


    # Assert: Verify TaskTeam was created by the handler
    task_team = await tasks_uow.repos.team.get_by_id(team.id)

    assert task_team is not None, "TaskTeam should be created"
    assert task_team.id == team.id, "TaskTeam ID should match Team ID"
    # assert task_team.members == [], "TaskTeam should have empty members list"
