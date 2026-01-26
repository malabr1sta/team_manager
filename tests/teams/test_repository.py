import pytest
from app.teams import (
    models,
    orm_models,
    repository
)


@pytest.mark.anyio
async def test_get_by_id(async_session):
    repo = repository.SQLAlchemyTeamRepository(async_session)

    team = orm_models.TeamOrm(name="Test Team")
    async_session.add(team)
    await async_session.commit()

    result = await repo.get_by_id(team.id)
    assert result is not None
    assert isinstance(result, models.Team)
    assert result._name == "Test Team"
    assert result.id
