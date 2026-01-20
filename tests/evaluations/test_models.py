from datetime import datetime, timedelta

from app.core.custom_types import ids, task_status
from app.evaluations import models, management
from app.evaluations.custom_exception import (
    EvaluationException,
    EvaluationSupervisorException
)

import pytest


class TestEvaluation:

    def test_create_evaluation(self):
        supervisor_id = ids.UserId(1)
        executor_id = ids.UserId(2)
        other_member = ids.UserId(3)
        task1 = models.Task(
            ids.TaskId(1), ids.TeamId(2),
            supervisor_id, executor_id, task_status.TaskStatus.DONE
        )
        task2 = models.Task(
            ids.TaskId(2), ids.TeamId(2),
            supervisor_id, executor_id, task_status.TaskStatus.IN_PROGRESS
        )
        evaluation = management.create_evaluation(
            supervisor_id, task1, 3
        )
        assert evaluation.user_id == executor_id
        assert evaluation.task_id == 1
        assert evaluation.grade == 3
        assert evaluation.team_id == 2
        assert evaluation.created_at

        with pytest.raises(EvaluationException):
            management.create_evaluation(
                        supervisor_id, task2, 3
                    )
        with pytest.raises(EvaluationSupervisorException):
            management.create_evaluation(
                        other_member, task1, 3
                    )

    def test_get_evaluation(self, get_user_evaluations):
        user: models.User = get_user_evaluations
        assert len(user.get_evaluations()) == 6
        assert len(user.get_evaluations(team_id=ids.TeamId(101))) == 4

    def test_average_grade(self, get_user_evaluations):
        user: models.User = get_user_evaluations
        average_grade_team1 = user.average_grade(team_id=ids.TeamId(101))
        assert average_grade_team1 == 4

        now = datetime.now()
        start = now - timedelta(days=7)
        end = now - timedelta(days=4)

        result = user.average_grade(
            team_id=ids.TeamId(101),
            start=start,
            end=end,
        )
        assert result == 3.5
