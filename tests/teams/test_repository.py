import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.teams import (
    models,
    orm_models,
    mappers,
)
from app.core.custom_types import ids, role
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork
)



@pytest.mark.anyio
async def test_get_by_id(teams_uow: TeamSQLAlchemyUnitOfWork):
    repo = teams_uow.repos.team
    async_session = teams_uow.session

    team_domain = models.Team(
        id=None,
        name="Test Team",
        members=[
            models.Member(
                user_id=ids.UserId(1),
                team_id=None,
                role=role.UserRole.MEMBER
            ),
            models.Member(
                user_id=ids.UserId(2),
                team_id=None,
                role=role.UserRole.ADMIN
            ),
        ]
    )
    team_orm = mappers.TeamMapper.to_orm(team_domain)
    async_session.add(team_orm)
    await async_session.commit()

    result = await repo.get_by_id(team_orm.id)

    assert result is not None
    assert isinstance(result, models.Team)
    assert result._name == "Test Team"
    assert result.id
    for member in result.members:
        assert member.team_id
        assert member.user_id
        assert member.role


@pytest.mark.anyio
async def test_save_creates_team(teams_uow: TeamSQLAlchemyUnitOfWork):
    repo = teams_uow.repos.team
    async_session = teams_uow.session

    team_domain = models.Team(
        id=None,
        name="New Team",
        members=[
            models.Member(
                user_id=ids.UserId(1),
                team_id=None,
                role=role.UserRole.MEMBER,
            ),
            models.Member(
                user_id=ids.UserId(2),
                team_id=None,
                role=role.UserRole.ADMIN,
            ),
        ],
    )

    await repo.save(team_domain)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TeamOrm).options(
            selectinload(orm_models.TeamOrm.members)
        )
    )
    team_orm = result.scalar_one()

    assert team_orm.id is not None
    assert team_orm.name == "New Team"
    assert len(team_orm.members) == 2

    roles = {member.role for member in team_orm.members}
    assert role.UserRole.MEMBER in roles
    assert role.UserRole.ADMIN in roles


@pytest.mark.anyio
async def test_get_by_user_returns_all_members(
        teams_uow: TeamSQLAlchemyUnitOfWork
):
    repo = teams_uow.repos.member
    async_session = teams_uow.session

    orm_members = [
        orm_models.MemberOrm(
            user_id=1,
            team_id=10,
            role=role.UserRole.MEMBER.value,
        ),
        orm_models.MemberOrm(
            user_id=1,
            team_id=20,
            role=role.UserRole.ADMIN.value,
        ),
        orm_models.MemberOrm(
            user_id=2,
            team_id=10,
            role=role.UserRole.MEMBER.value,
        ),
    ]

    async_session.add_all(orm_members)
    await async_session.commit()

    members = await repo.get_by_user(user_id=1)

    assert len(members) == 2
    assert {m.team_id for m in members} == {10, 20}
    assert all(m.user_id == 1 for m in members)


@pytest.mark.anyio
async def test_get_by_user_and_team(teams_uow: TeamSQLAlchemyUnitOfWork):
    repo = teams_uow.repos.member
    async_session = teams_uow.session

    orm_member = orm_models.MemberOrm(
        user_id=1,
        team_id=10,
        role=role.UserRole.ADMIN.value,
    )

    async_session.add(orm_member)
    await async_session.commit()

    member = await repo.get_by_user_and_team(
        user_id=1,
        team_id=10,
    )

    assert member is not None
    assert member.user_id == 1
    assert member.team_id == 10
    assert member.role == role.UserRole.ADMIN


@pytest.mark.anyio
async def test_get_by_user_and_team_returns_none(
        teams_uow: TeamSQLAlchemyUnitOfWork
):
    repo = teams_uow.repos.member

    member = await repo.get_by_user_and_team(
        user_id=999,
        team_id=10,
    )

    assert member is None


@pytest.mark.anyio
async def test_save_creates_member(teams_uow: TeamSQLAlchemyUnitOfWork):
    repo = teams_uow.repos.member
    async_session = teams_uow.session

    member = models.Member(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(10),
        role=role.UserRole.MEMBER,
    )

    await repo.save(member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.MemberOrm)
    )
    orm_members = result.scalars().all()

    assert len(orm_members) == 1
    assert orm_members[0].user_id == 1
    assert orm_members[0].team_id == 10
    assert orm_members[0].role == role.UserRole.MEMBER


@pytest.mark.anyio
async def test_save_updates_existing_member(
        teams_uow: TeamSQLAlchemyUnitOfWork
):
    repo = teams_uow.repos.member
    async_session = teams_uow.session

    orm_member = orm_models.MemberOrm(
        user_id=1,
        team_id=10,
        role=role.UserRole.MEMBER.value,
    )

    async_session.add(orm_member)
    await async_session.commit()

    updated_member = models.Member(
        user_id=ids.UserId(1),
        team_id=ids.TeamId(10),
        role=role.UserRole.ADMIN,
    )

    await repo.save(updated_member)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.MemberOrm)
        .where(
            orm_models.MemberOrm.user_id == 1,
            orm_models.MemberOrm.team_id == 10,
        )
    )
    orm_member = result.scalar_one()

    assert orm_member.role == role.UserRole.ADMIN


@pytest.mark.anyio
async def test_user_repository_save(teams_uow: TeamSQLAlchemyUnitOfWork):
    repo = teams_uow.repos.user
    async_session = teams_uow.session

    user = models.User(ids.UserId(1))
    await repo.save(user)
    await async_session.commit()

    result = await async_session.execute(select(orm_models.TeamUserOrm))
    users = result.scalars().all()

    assert len(users) == 1
    assert users[0].id == 1

    user_2 = models.User(ids.UserId(2))
    await repo.save(user_2)
    await async_session.commit()

    result = await async_session.execute(select(orm_models.TeamUserOrm))
    users = result.scalars().all()

    assert len(users) == 2
    assert {u.id for u in users} == {1, 2}
