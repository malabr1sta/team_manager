import pytest
from fastapi import status


@pytest.mark.anyio
async def test_register_user(client):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "username": "testuser"
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


@pytest.mark.anyio
async def test_full_flow(client):
    """Test complete flow: register -> login -> create team -> get team."""
    # 1. Register
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "flow@example.com",
            "password": "FlowPass123!",
            "username": "flowuser"
        }
    )
    assert register_response.status_code == status.HTTP_201_CREATED

    # 2. Login
    login_response = await client.post(
        "/api/v1/auth/jwt/login",
        data={
            "username": "flow@example.com",
            "password": "FlowPass123!"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]

    # 3. /me
    get_response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == status.HTTP_200_OK
    user_data = get_response.json()
    assert user_data["email"] == "flow@example.com"
    assert user_data["username"] == "flowuser"

    # 4. Create team
    create_team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Test Team"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_team_response.status_code == status.HTTP_201_CREATED
    admin_id = create_team_response.json()["admin_user_id"]
    assert admin_id

    create_team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Test Team"},
    )
    assert create_team_response.status_code == status.HTTP_401_UNAUTHORIZED
