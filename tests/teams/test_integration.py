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


async def _register_and_login(client, idx: int) -> str:
    email = f"user{idx}@example.com"
    password = f"Password{idx}23!"
    username = f"user{idx}"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "username": username,
        },
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    login_response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == status.HTTP_200_OK
    return login_response.json()["access_token"]


@pytest.mark.anyio
async def test_admin_can_add_member(client):
    admin_token = await _register_and_login(client, 10)
    member_token = await _register_and_login(client, 11)

    team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Core Team"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert team_response.status_code == status.HTTP_201_CREATED
    team_id = team_response.json()["team_id"]

    me_member = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    member_id = me_member.json()["id"]

    add_response = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert add_response.status_code == status.HTTP_200_OK
    roles = {member["role"] for member in add_response.json()["members"]}
    assert "member" in roles

    member_get_response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert member_get_response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_non_admin_cannot_add_member(client):
    admin_token = await _register_and_login(client, 20)
    member_token = await _register_and_login(client, 21)
    another_token = await _register_and_login(client, 22)

    team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Ops Team"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    team_id = team_response.json()["team_id"]

    me_member = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    member_id = me_member.json()["id"]
    me_another = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {another_token}"},
    )
    another_id = me_another.json()["id"]

    add_member_response = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert add_member_response.status_code == status.HTTP_200_OK

    forbidden_response = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": another_id, "role": "member"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_admin_can_change_member_role(client):
    admin_token = await _register_and_login(client, 30)
    member_token = await _register_and_login(client, 31)

    team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Platform Team"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    team_id = team_response.json()["team_id"]

    me_member = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    member_id = me_member.json()["id"]

    await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    change_role_response = await client.patch(
        f"/api/v1/teams/{team_id}/members/{member_id}/role",
        json={"old_role": "member", "new_role": "manager"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert change_role_response.status_code == status.HTTP_200_OK
    members = change_role_response.json()["members"]
    assert any(m["user_id"] == member_id and m["role"] == "manager" for m in members)


@pytest.mark.anyio
async def test_admin_can_remove_member(client):
    admin_token = await _register_and_login(client, 40)
    member_token = await _register_and_login(client, 41)

    team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Delivery Team"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    team_id = team_response.json()["team_id"]

    me_member = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    member_id = me_member.json()["id"]

    await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    remove_response = await client.delete(
        f"/api/v1/teams/{team_id}/members/{member_id}",
        params={"role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert remove_response.status_code == status.HTTP_200_OK

    member_get_response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert member_get_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_non_member_cannot_get_team(client):
    admin_token = await _register_and_login(client, 50)
    outsider_token = await _register_and_login(client, 51)

    team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Security Team"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    team_id = team_response.json()["team_id"]

    outsider_response = await client.get(
        f"/api/v1/teams/{team_id}",
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert outsider_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_register_event_creates_teams_user(client):
    token = await _register_and_login(client, 60)

    create_team_response = await client.post(
        "/api/v1/teams",
        json={"team_name": "Event Team"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_team_response.status_code == status.HTTP_201_CREATED
