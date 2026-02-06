import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tasks import (
    models,
    orm_models,
    mappers,
    repository
)
from app.core.custom_types import ids, role


@pytest.mark.anyio
async def test_save_creates_new_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskUserOrm)
        .where(orm_models.TaskUserOrm.id == 1)
    )
    orm_user = result.scalar_one()

    assert orm_user.id == 1
    assert orm_user.username == "leonya"


@pytest.mark.anyio
async def test_get_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    user_1 = await repo.get_by_id(1)

    assert user_1
    assert user_1.id == 1
    assert user_1.username == "leonya"


@pytest.mark.anyio
async def test_save_creates_new_member(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)
    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskMemberOrm)
        .where(
            orm_models.TaskMemberOrm.user_id == 1,
            orm_models.TaskMemberOrm.team_id == 1
        )
    )
    orm_member = result.scalar_one()

    assert orm_member.user_id == 1
    assert orm_member.team_id == 1
    assert orm_member.role == role.UserTaskRole.MEMBER


@pytest.mark.anyio
async def test_save_updates_existing_member(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    same_member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(same_member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskMemberOrm)
        .where(
            orm_models.TaskMemberOrm.user_id == 1,
            orm_models.TaskMemberOrm.team_id == 1,
            orm_models.TaskMemberOrm.role == role.UserTaskRole.MEMBER
        )
    )
    all_members = result.scalars().all()
    assert len(all_members) == 1


@pytest.mark.anyio
async def test_save_creates_multiple_roles_for_same_user_and_team(async_session):
    """We check that a user can have multiple roles in one team"""
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    await repo.save(member1)

    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MANAGER
    )
    await repo.save(member2)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 2
    roles = {member.role for member in members}
    assert roles == {role.UserTaskRole.MEMBER, role.UserTaskRole.MANAGER}


@pytest.mark.anyio
async def test_get_by_user_returns_all_roles(async_session):
    """We check that get_by_user returns all user roles in all commands"""
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MANAGER
    )
    member3 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member1)
    await repo.save(member2)
    await repo.save(member3)
    await async_session.commit()

    members = await repo.get_by_user(1)

    assert len(members) == 3


@pytest.mark.anyio
async def test_get_by_user(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MANAGER
    )

    await repo.save(member1)
    await repo.save(member2)
    await async_session.commit()

    members = await repo.get_by_user(1)

    assert len(members) == 2
    assert all(member.user_id == 1 for member in members)
    team_ids = {member.team_id for member in members}
    assert team_ids == {1, 2}


@pytest.mark.anyio
async def test_get_by_user_empty_result(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    members = await repo.get_by_user(999)

    assert members == []


@pytest.mark.anyio
async def test_get_by_user_and_team(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 1
    assert members[0].user_id == 1
    assert members[0].team_id == 1
    assert members[0].role == role.UserTaskRole.MEMBER


@pytest.mark.anyio
async def test_get_by_user_and_team_empty_result(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 999)

    assert members == []


@pytest.mark.anyio
async def test_get_by_user_and_team_filters_correctly(async_session):
    repo = repository.SQLAlchemyTaskMemberRepository(async_session)

    member1 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )
    member2 = models.MemberTask(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(2),
        role=role.UserTaskRole.MANAGER
    )
    member3 = models.MemberTask(
        user_id=ids.UserId(2),
        team_id=ids.TeamId(1),
        role=role.UserTaskRole.MEMBER
    )

    await repo.save(member1)
    await repo.save(member2)
    await repo.save(member3)
    await async_session.commit()

    members = await repo.get_by_user_and_team(1, 1)

    assert len(members) == 1
    assert members[0].user_id == 1
    assert members[0].team_id == 1


@pytest.mark.anyio
async def test_save_creates_new_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)
    team = models.Team(
        id=ids.TeamId(100),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    orm_team = result.scalar_one()

    assert orm_team.id == 100


@pytest.mark.anyio
async def test_save_updates_existing_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(100),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    updated_team = models.Team(
        id=ids.TeamId(100),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(100),
                role=role.UserTaskRole.MEMBER
            )
        ]
    )

    await repo.save(updated_team)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    orm_team = result.scalar_one()

    assert orm_team.id == 100

    result_all = await async_session.execute(
        select(orm_models.TaskTeamOrm)
        .where(orm_models.TaskTeamOrm.id == 100)
    )
    all_teams = result_all.scalars().all()
    assert len(all_teams) == 1


@pytest.mark.anyio
async def test_get_by_id_returns_team(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(200),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(200),
                role=role.UserTaskRole.MANAGER
            )
        ]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(200)

    assert found_team is not None
    assert found_team.id == 200
    assert len(found_team.members) == 1
    assert found_team.members[0].user_id == 1
    assert found_team.members[0].role == role.UserTaskRole.MANAGER


@pytest.mark.anyio
async def test_get_by_id_returns_none_if_not_found(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    found_team = await repo.get_by_id(999)

    assert found_team is None


@pytest.mark.anyio
async def test_save_team_with_multiple_members(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(300),
        members=[
            models.MemberTask(
                user_id=ids.UserId(1),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MANAGER
            ),
            models.MemberTask(
                user_id=ids.UserId(2),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MEMBER
            ),
            models.MemberTask(
                user_id=ids.UserId(3),
                team_id=ids.TeamId(300),
                role=role.UserTaskRole.MEMBER
            )
        ]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(300)

    assert found_team is not None
    assert found_team.id == 300
    assert len(found_team.members) == 3

    user_ids = {member.user_id for member in found_team.members}
    assert user_ids == {1, 2, 3}


@pytest.mark.anyio
async def test_save_team_with_empty_members(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team = models.Team(
        id=ids.TeamId(400),
        members=[]
    )

    await repo.save(team)
    await async_session.commit()

    found_team = await repo.get_by_id(400)

    assert found_team is not None
    assert found_team.id == 400
    assert len(found_team.members) == 0


@pytest.mark.anyio
async def test_save_multiple_teams_with_different_ids(async_session):
    repo = repository.SQLAlchemyTeamMemberRepository(async_session)

    team1 = models.Team(
        id=ids.TeamId(100),
        members=[]
    )
    team2 = models.Team(
        id=ids.TeamId(200),
        members=[]
    )

    await repo.save(team1)
    await repo.save(team2)
    await async_session.commit()

    found_team1 = await repo.get_by_id(100)
    found_team2 = await repo.get_by_id(200)

    assert found_team1 is not None
    assert found_team1.id == 100
    assert found_team2 is not None
    assert found_team2.id == 200
