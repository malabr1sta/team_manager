from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status


async def _register_and_login(client, idx: int) -> tuple[int, str]:
    email = f"scheduling_user_{idx}@example.com"
    password = f"SchedulingPass{idx}123!"
    username = f"scheduling_user_{idx}"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "username": username,
        },
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    user_id = register_response.json()["id"]
    login_response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == status.HTTP_200_OK
    return user_id, login_response.json()["access_token"]


async def _create_team(client, admin_token: str, team_name: str) -> int:
    response = await client.post(
        "/api/v1/teams",
        json={"team_name": team_name},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    return response.json()["team_id"]


async def _add_member(
        client,
        team_id: int,
        admin_token: str,
        member_id: int,
        role: str,
) -> None:
    response = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": role},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_manager_can_create_list_and_cancel_meeting(client):
    _, admin_token = await _register_and_login(client, 1)
    manager_id, manager_token = await _register_and_login(client, 2)
    member_id, member_token = await _register_and_login(client, 3)

    team_id = await _create_team(client, admin_token, "Scheduling Team")
    await _add_member(client, team_id, admin_token, manager_id, "manager")
    await _add_member(client, team_id, admin_token, member_id, "member")

    start = datetime.now(timezone.utc) + timedelta(hours=3)
    end = start + timedelta(hours=1)
    create_response = await client.post(
        "/api/v1/scheduling/meetings",
        json={
            "team_id": team_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": "Sprint planning",
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    meeting_id = create_response.json()["id"]

    add_participant_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert add_participant_response.status_code == status.HTTP_200_OK
    participants = add_participant_response.json()["participants"]
    assert any(item["user_id"] == member_id for item in participants)

    list_response = await client.get(
        f"/api/v1/scheduling/meetings?team_id={team_id}&limit=10&offset=0",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.json()["total"] == 1

    remove_participant_response = await client.delete(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert remove_participant_response.status_code == status.HTTP_200_OK
    participants = remove_participant_response.json()["participants"]
    assert all(item["user_id"] != member_id for item in participants)

    cancel_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/cancel",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert cancel_response.status_code == status.HTTP_200_OK
    assert cancel_response.json()["is_cancelled"] is True


@pytest.mark.anyio
async def test_non_manager_cannot_create_meeting(client):
    _, admin_token = await _register_and_login(client, 11)
    member_id, member_token = await _register_and_login(client, 12)

    team_id = await _create_team(client, admin_token, "Scheduling Team 2")
    await _add_member(client, team_id, admin_token, member_id, "member")

    start = datetime.now(timezone.utc) + timedelta(hours=4)
    end = start + timedelta(hours=1)
    response = await client.post(
        "/api/v1/scheduling/meetings",
        json={
            "team_id": team_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": "Should fail",
        },
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_non_organizer_cannot_manage_participants_or_cancel(client):
    _, admin_token = await _register_and_login(client, 21)
    manager_id, manager_token = await _register_and_login(client, 22)
    member_id, member_token = await _register_and_login(client, 23)

    team_id = await _create_team(client, admin_token, "Scheduling Team 3")
    await _add_member(client, team_id, admin_token, manager_id, "manager")
    await _add_member(client, team_id, admin_token, member_id, "member")

    start = datetime.now(timezone.utc) + timedelta(hours=5)
    end = start + timedelta(hours=1)
    create_response = await client.post(
        "/api/v1/scheduling/meetings",
        json={
            "team_id": team_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": "Access control test",
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    meeting_id = create_response.json()["id"]

    add_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{manager_id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert add_response.status_code == status.HTTP_403_FORBIDDEN

    remove_response = await client.delete(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{manager_id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert remove_response.status_code == status.HTTP_403_FORBIDDEN

    cancel_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/cancel",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert cancel_response.status_code == status.HTTP_403_FORBIDDEN
