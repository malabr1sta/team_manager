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
    """Проверяем, что пользователь может иметь несколько ролей в одной команде"""
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
    """Проверяем, что get_by_user возвращает все роли пользователя во всех командах"""
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

