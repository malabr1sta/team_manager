from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status


async def _register_and_login(client, idx: int) -> tuple[int, str]:
    email = f"evaluation_user_{idx}@example.com"
    password = f"EvaluationPass{idx}123!"
    username = f"evaluation_user_{idx}"
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
async def test_supervisor_can_create_evaluation_and_member_can_read_it(client):
    admin_id, admin_token = await _register_and_login(client, 1)
    manager_id, manager_token = await _register_and_login(client, 2)
    member_id, member_token = await _register_and_login(client, 3)

    team_id = await _create_team(client, admin_token, "Evaluation Team")
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

    deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_task_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Performance check",
            "description": "Prepare release metrics",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_task_response.status_code == status.HTTP_201_CREATED
    task_id = create_task_response.json()["id"]

    assign_response = await client.post(
        f"/api/v1/tasks/{task_id}/executor/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert assign_response.status_code == status.HTTP_200_OK

    done_response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        json={"status": "done"},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert done_response.status_code == status.HTTP_200_OK

    create_evaluation_response = await client.post(
        f"/api/v1/evaluations/tasks/{task_id}",
        json={"grade": 5},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_evaluation_response.status_code == status.HTTP_201_CREATED
    payload = create_evaluation_response.json()
    assert payload["task_id"] == task_id
    assert payload["user_id"] == member_id
    assert payload["team_id"] == team_id
    assert payload["grade"] == 5

    list_my_response = await client.get(
        "/api/v1/evaluations/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert list_my_response.status_code == status.HTTP_200_OK
    list_payload = list_my_response.json()
    assert list_payload["total"] == 1
    assert list_payload["items"][0]["task_id"] == task_id

    average_response = await client.get(
        f"/api/v1/evaluations/me/average?team_id={team_id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert average_response.status_code == status.HTTP_200_OK
    assert average_response.json()["average"] == 5.0

    not_supervisor_response = await client.post(
        f"/api/v1/evaluations/tasks/{task_id}",
        json={"grade": 4},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert not_supervisor_response.status_code == status.HTTP_403_FORBIDDEN
    assert admin_id != manager_id


@pytest.mark.anyio
async def test_cannot_create_evaluation_for_not_done_task(client):
    _, admin_token = await _register_and_login(client, 11)
    manager_id, manager_token = await _register_and_login(client, 12)
    member_id, _ = await _register_and_login(client, 13)

    team_id = await _create_team(client, admin_token, "Evaluation Team 2")
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
    create_task_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Not done task",
            "description": "This task stays open",
            "deadline": deadline,
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_task_response.status_code == status.HTTP_201_CREATED
    task_id = create_task_response.json()["id"]

    await client.post(
        f"/api/v1/tasks/{task_id}/executor/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    response = await client.post(
        f"/api/v1/evaluations/tasks/{task_id}",
        json={"grade": 3},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
