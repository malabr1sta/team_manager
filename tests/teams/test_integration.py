import pytest

from fastapi import status


@pytest.mark.anyio
async def test_get_team_as_member(authenticated_client, test_team):
    """Test getting team details as a member."""
    response = await authenticated_client.get(
        f"/api/v1/teams/{test_team['team_id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_team["team_id"]
    assert data["is_member"] is True
