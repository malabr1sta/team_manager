from datetime import datetime, timezone, timedelta

import pytest
from fastapi import status


async def _register_and_login(client, idx: int) -> tuple[int, str]:
    email = f"task_user_{idx}@example.com"
    password = f"TaskPass{idx}123!"
    username = f"task_user_{idx}"
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
    token = login_response.json()["access_token"]
    return user_id, token


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
    *,
    team_id: int,
    admin_token: str,
    member_id: int,
    role: str,
):
    response = await client.post(
        f"/api/v1/teams/{team_id}/members",
        json={"target_user_id": member_id, "role": role},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_manager_can_create_and_list_tasks(client):
    _, admin_token = await _register_and_login(client, 1)
    manager_id, manager_token = await _register_and_login(client, 2)
    team_id = await _create_team(client, admin_token, "Task Team A")
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=manager_id,
        role="manager",
    )

    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Prepare report",
            "description": "Quarterly planning report",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    data = create_response.json()
    assert data["title"] == "Prepare report"
    assert data["team_id"] == team_id

    list_response = await client.get(
        f"/api/v1/tasks?team_id={team_id}&limit=10&offset=0",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert list_response.status_code == status.HTTP_200_OK
    list_data = list_response.json()
    assert list_data["total"] == 1
    assert len(list_data["items"]) == 1


@pytest.mark.anyio
async def test_member_cannot_create_task(client):
    _, admin_token = await _register_and_login(client, 10)
    member_id, member_token = await _register_and_login(client, 11)
    team_id = await _create_team(client, admin_token, "Task Team B")
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=member_id,
        role="member",
    )

    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Should fail",
            "description": "Only manager can create",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_supervisor_can_assign_and_update_task(client):
    _, admin_token = await _register_and_login(client, 20)
    manager_id, manager_token = await _register_and_login(client, 21)
    member_id, _ = await _register_and_login(client, 22)
    team_id = await _create_team(client, admin_token, "Task Team C")
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=manager_id,
        role="manager",
    )
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=member_id,
        role="member",
    )

    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Implement endpoint",
            "description": "Add task endpoint",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    task_id = create_response.json()["id"]

    assign_response = await client.post(
        f"/api/v1/tasks/{task_id}/executor/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert assign_response.status_code == status.HTTP_200_OK
    assert assign_response.json()["executor_id"] == member_id

    update_response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "in_progress", "deleted": True},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated = update_response.json()
    assert updated["status"] == "in_progress"
    assert updated["deleted"] is True


@pytest.mark.anyio
async def test_non_supervisor_cannot_update_task(client):
    _, admin_token = await _register_and_login(client, 30)
    manager_id, manager_token = await _register_and_login(client, 31)
    member_id, member_token = await _register_and_login(client, 32)
    team_id = await _create_team(client, admin_token, "Task Team D")
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=manager_id,
        role="manager",
    )
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=member_id,
        role="member",
    )

    deadline = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Ownership test",
            "description": "Only supervisor may update",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"title": "Hacked"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_comments_allowed_only_for_team_members(client):
    _, admin_token = await _register_and_login(client, 40)
    manager_id, manager_token = await _register_and_login(client, 41)
    member_id, member_token = await _register_and_login(client, 42)
    _, outsider_token = await _register_and_login(client, 43)
    team_id = await _create_team(client, admin_token, "Task Team E")
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=manager_id,
        role="manager",
    )
    await _add_member(
        client,
        team_id=team_id,
        admin_token=admin_token,
        member_id=member_id,
        role="member",
    )

    deadline = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Discuss architecture",
            "description": "Need comments",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    task_id = create_response.json()["id"]

    comment_response = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"text": "I can work on this"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert comment_response.status_code == status.HTTP_201_CREATED

    outsider_response = await client.post(
        f"/api/v1/tasks/{task_id}/comments",
        json={"text": "I should not post"},
        headers={"Authorization": f"Bearer {outsider_token}"},
    )
    assert outsider_response.status_code == status.HTTP_403_FORBIDDEN

    list_response = await client.get(
        f"/api/v1/tasks/{task_id}/comments",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.json()) == 1
