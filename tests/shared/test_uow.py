import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.teams import (
    models,
    orm_models,
    mappers,
)
from app.core.custom_types import ids, role
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork,
    TeamRepositoryProvider
)
from app.core.infrastructure.event_bus import EventBus


@pytest.mark.anyio
async def test_uow_context_manager(
    async_session_factory: async_sessionmaker[AsyncSession],
    event_bus: EventBus
):
    """Test that UoW properly initializes repos
    and manages session lifecycle."""
    async with TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    ) as uow:
        # Verify session and repos are initialized
        assert uow.session is not None
        assert isinstance(uow.session, AsyncSession)
        assert uow.repos is not None
        assert isinstance(uow.repos, TeamRepositoryProvider)

        # Verify all lazy repos are accessible
        assert uow.repos.team is not None
        assert uow.repos.member is not None
        assert uow.repos.user is not None


@pytest.mark.anyio
async def test_uow_commit_persists_data(
    async_session_factory: async_sessionmaker[AsyncSession],
    event_bus: EventBus
):
    """Test that commit() persists changes to the database."""
    team_id = None

    # Create and commit a team
    async with TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    ) as uow:
        user = models.User(ids.UserId(1))
        await uow.repos.user.save(user)
        await uow.commit()
        team_domain = models.Team(
            id=None,
            name="Test Team",
            members=[
                models.Member(
                    user_id=ids.UserId(1),
                    team_id=None,
                    role=role.UserRole.MEMBER
                ),
            ]
        )
        team_orm = mappers.TeamMapper.to_orm(team_domain)
        uow.session.add(team_orm)
        await uow.commit()
        team_id = team_orm.id

    # Verify data persists in new session
    async with TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    ) as uow:
        result = await uow.repos.team.get_by_id(team_id)
        assert result is not None
        assert result._name == "Test Team"
        assert len(result.members) == 1


@pytest.mark.anyio
async def test_uow_rollback_on_exception(
    async_session_factory: async_sessionmaker[AsyncSession],
    event_bus: EventBus
):
    """Test that changes are rolled back when exception occurs."""
    with pytest.raises(ValueError):
        async with TeamSQLAlchemyUnitOfWork(
            session_factory=async_session_factory,
            bus=event_bus,
            provider_cls=TeamRepositoryProvider
        ) as uow:
            team_domain = models.Team(
                id=None,
                name="Test Team",
                members=[]
            )
            team_orm = mappers.TeamMapper.to_orm(team_domain)
            uow.session.add(team_orm)
            # Raise exception before commit
            raise ValueError("Test exception")

    # Verify no data was persisted
    async with TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    ) as uow:
        result = await uow.session.execute(
            select(orm_models.TeamOrm)
        )
        teams = result.scalars().all()
        assert len(teams) == 0
