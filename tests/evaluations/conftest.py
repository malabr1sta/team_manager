import pytest
from datetime import datetime, timedelta

from app.evaluations.models import Evaluation, User
from app.core.custom_types import ids


@pytest.fixture
def get_user_evaluations() -> User:
    user_id = ids.UserId(1)
    team1 = ids.TeamId(101)
    team2 = ids.TeamId(102)
    task1 = ids.TaskId(201)
    task2 = ids.TaskId(202)

    now = datetime.now()

    evaluations = [
        Evaluation(
            user_id=user_id, team_id=team1, task_id=task1,
            grade=5,
            created_at=now - timedelta(days=10)
        ),
        Evaluation(
            user_id=user_id, team_id=team1, task_id=task2,
            grade=3, created_at=now - timedelta(days=5)
        ),
        Evaluation(
            user_id=user_id, team_id=team1, task_id=task2,
            grade=4, created_at=now - timedelta(days=6)
        ),
        Evaluation(
            user_id=user_id, team_id=team1, task_id=task2,
            grade=4, created_at=now - timedelta(days=8)
        ),
        Evaluation(
            user_id=user_id, team_id=team2, task_id=task1,
            grade=4,
            created_at=now - timedelta(days=7)),
        Evaluation(
            user_id=user_id, team_id=team2, task_id=task2,
            grade=2,
            created_at=now - timedelta(days=1)
        ),
    ]

    return User(id=user_id, evaluations=evaluations)
