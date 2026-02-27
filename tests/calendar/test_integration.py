from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status


async def _register_and_login(client, idx: int) -> tuple[int, str]:
    email = f"calendar_user_{idx}@example.com"
    password = f"CalendarPass{idx}123!"
    username = f"calendar_user_{idx}"
    register_response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "username": username},
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
async def test_calendar_day_and_month_include_task_and_meeting_events(client):
    _, admin_token = await _register_and_login(client, 1)
    manager_id, manager_token = await _register_and_login(client, 2)
    member_id, member_token = await _register_and_login(client, 3)

    team_id = await _create_team(client, admin_token, "Calendar Team")
    await _add_member(client, team_id, admin_token, manager_id, "manager")
    await _add_member(client, team_id, admin_token, member_id, "member")

    deadline = datetime.now(timezone.utc) + timedelta(days=1)
    create_task_response = await client.post(
        "/api/v1/tasks",
        json={
            "team_id": team_id,
            "title": "Calendar task",
            "description": "Task for calendar",
            "deadline": deadline.isoformat(),
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

    start = datetime.now(timezone.utc) + timedelta(days=1, hours=1)
    end = start + timedelta(hours=1)
    create_meeting_response = await client.post(
        "/api/v1/scheduling/meetings",
        json={
            "team_id": team_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": "Calendar meeting",
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_meeting_response.status_code == status.HTTP_201_CREATED
    meeting_id = create_meeting_response.json()["id"]

    add_member_meeting_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert add_member_meeting_response.status_code == status.HTTP_200_OK

    target_day = start.date().isoformat()
    day_response = await client.get(
        f"/api/v1/calendar/day?day={target_day}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert day_response.status_code == status.HTTP_200_OK
    items = day_response.json()["items"]
    types = {item["event_type"] for item in items}
    assert "task" in types
    assert "meeting" in types

    month_response = await client.get(
        f"/api/v1/calendar/month?year={start.year}&month={start.month}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert month_response.status_code == status.HTTP_200_OK
    assert month_response.json()["total"] >= 2


@pytest.mark.anyio
async def test_cancelled_meeting_is_hidden_from_calendar_views(client):
    _, admin_token = await _register_and_login(client, 11)
    manager_id, manager_token = await _register_and_login(client, 12)
    member_id, member_token = await _register_and_login(client, 13)

    team_id = await _create_team(client, admin_token, "Calendar Team 2")
    await _add_member(client, team_id, admin_token, manager_id, "manager")
    await _add_member(client, team_id, admin_token, member_id, "member")

    start = datetime.now(timezone.utc) + timedelta(days=2, hours=1)
    end = start + timedelta(hours=1)
    create_meeting_response = await client.post(
        "/api/v1/scheduling/meetings",
        json={
            "team_id": team_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "description": "Meeting to cancel",
        },
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert create_meeting_response.status_code == status.HTTP_201_CREATED
    meeting_id = create_meeting_response.json()["id"]

    await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/participants/{member_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
    )

    cancel_response = await client.post(
        f"/api/v1/scheduling/meetings/{meeting_id}/cancel",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert cancel_response.status_code == status.HTTP_200_OK

    target_day = start.date().isoformat()
    day_response = await client.get(
        f"/api/v1/calendar/day?day={target_day}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert day_response.status_code == status.HTTP_200_OK
    assert day_response.json()["items"] == []
