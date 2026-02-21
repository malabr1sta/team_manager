import pytest

from app.core.custom_types import ids, role
from app.teams import (
    management as teams_management,
    models as teams_models
)
from app.teams.unit_of_work import TeamSQLAlchemyUnitOfWork
from app.tasks.unit_of_work import (
    TaskSQLAlchemyUnitOfWork,
)
from app.tasks import models as tasks_models


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

    user = teams_models.User(user_id)

    await teams_uow.repos.user.save(user)
    await teams_uow.commit()
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


@pytest.mark.anyio
async def test_task_team_add_member(
    created_team: teams_models.Team,
    teams_uow: TeamSQLAlchemyUnitOfWork,
    tasks_uow: TaskSQLAlchemyUnitOfWork,
    init_user
):
    team = created_team
    user_id_admin = ids.UserId(10)
    user_id_member = ids.UserId(11)
    user_id_manager = ids.UserId(12)
    assert team.id is not None
    team.add_member(user_id=user_id_member, role_member=role.UserRole.MEMBER)
    team.add_member(user_id=user_id_manager, role_member=role.UserRole.MANAGER)
    team.add_member(user_id=user_id_admin, role_member=role.UserRole.ADMIN)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    member = tasks_models.MemberTask(
        user_id_member, team_task.id, role.UserTaskRole.MEMBER
    )
    assert member == team_task.get_member(
        user_id_member, role.UserTaskRole.MEMBER
    )
    manager = tasks_models.MemberTask(
        user_id_manager, team_task.id, role.UserTaskRole.MANAGER
    )
    assert manager == team_task.get_member(
        user_id_manager, role.UserTaskRole.MANAGER
    )
    assert len(team_task._members) == 2


@pytest.mark.anyio
async def test_task_team_remove_member(
    created_team: teams_models.Team,
    teams_uow: TeamSQLAlchemyUnitOfWork,
    tasks_uow: TaskSQLAlchemyUnitOfWork,
    init_user
):
    team = created_team
    user_id_admin = ids.UserId(10)
    user_id_member = ids.UserId(11)
    user_id_manager = ids.UserId(12)
    assert team.id is not None
    team.add_member(user_id=user_id_member, role_member=role.UserRole.MEMBER)
    team.add_member(user_id=user_id_manager, role_member=role.UserRole.MANAGER)
    team.add_member(user_id=user_id_admin, role_member=role.UserRole.ADMIN)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team.remove_member(user_id_admin, role.UserRole.ADMIN)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()
    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert len(team_task._members) == 2

    team.remove_member(user_id_member, role.UserRole.MEMBER)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert not team_task.has_member(user_id_member, role.UserTaskRole.MEMBER)

    team.remove_member(user_id_manager, role.UserRole.MANAGER)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert not team_task.has_member(user_id_manager, role.UserTaskRole.MANAGER)


@pytest.mark.anyio
async def test_task_team_change_role(
    created_team: teams_models.Team,
    teams_uow: TeamSQLAlchemyUnitOfWork,
    tasks_uow: TaskSQLAlchemyUnitOfWork,
    init_user
):
    team = created_team
    user_id_admin = ids.UserId(10)
    user_id_member = ids.UserId(11)
    user_id_manager = ids.UserId(12)
    assert team.id is not None
    team.add_member(user_id=user_id_member, role_member=role.UserRole.MEMBER)
    team.add_member(user_id=user_id_manager, role_member=role.UserRole.MANAGER)
    team.add_member(user_id=user_id_admin, role_member=role.UserRole.ADMIN)
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team.change_role(
        user_id_member,
        role.UserRole.MEMBER,
        role.UserRole.MANAGER
    )
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert team_task.has_member(user_id_member, role.UserTaskRole.MANAGER)
    assert not team_task.has_member(user_id_member, role.UserTaskRole.MEMBER)

    team.change_role(
        user_id_member,
        role.UserRole.MANAGER,
        role.UserRole.ADMIN
    )
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()

    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert len(team_task._members) == 1

    team.change_role(
        user_id_member,
        role.UserRole.ADMIN,
        role.UserRole.MEMBER
    )
    await teams_uow.repos.team.save(team)
    await teams_uow.commit()
    team_task = await tasks_uow.repos.team.get_by_id(team.id)
    assert team_task is not None
    assert len(team_task._members) == 2
