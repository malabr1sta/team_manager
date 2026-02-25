import pytest
from typing import AsyncGenerator
from fastapi import status

from app.teams import models as teams_models
from app.core.custom_types import role, ids
from app.teams.unit_of_work import (
    TeamSQLAlchemyUnitOfWork,
    TeamRepositoryProvider
)



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


@pytest.fixture(scope="function")
def teams_uow_factory(async_session_factory, event_bus):
    """Factory for Tasks UnitOfWork."""

    return TeamSQLAlchemyUnitOfWork(
        session_factory=async_session_factory,
        bus=event_bus,
        provider_cls=TeamRepositoryProvider
    )


@pytest.fixture
async def teams_uow(
        teams_uow_factory
) -> AsyncGenerator[TeamSQLAlchemyUnitOfWork, None]:
    """Tasks UnitOfWork with automatic context."""
    async with teams_uow_factory as uow:
        yield uow


@pytest.fixture
async def test_team(authenticated_client):
    """Create test team and return team data."""
    response = await authenticated_client.post(
        "/api/v1/teams",
        json={"team_name": "Test Team"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()
