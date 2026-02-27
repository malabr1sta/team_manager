from datetime import datetime, timezone
from app.core.custom_types import ids, task_status, grade
from app.core.entity import Entity
from app.core.shared.models.users import BaseUser
from app.evaluations import custom_exception

from dataclasses import dataclass


@dataclass(frozen=True)
class Evaluation:
    user_id: ids.UserId
    team_id: ids.TeamId
    task_id: ids.TaskId
    grade: grade.Grade
    created_at: datetime

    def matches(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        team_id: ids.TeamId | None = None
    ) -> bool:
        """Check if evaluation matches given filters."""
        if start and self.created_at < start:
            return False
        if end and self.created_at > end:
            return False
        if team_id and self.team_id != team_id:
            return False
        return True


class User(BaseUser):

    def __init__(
            self,
            id: ids.UserId,
            evaluations: list[Evaluation] | None = None,
            username: str = ""
    ):
        self.id = id
        self.username = username
        self._evaluations = evaluations if evaluations is not None else []

    @property
    def evaluations(self) -> tuple[Evaluation, ...]:
        """Return team evaluations as an immutable collection."""
        return tuple(self._evaluations)

    def get_evaluations(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        team_id: ids.TeamId | None = None
    ) -> list[Evaluation]:
        """
        Return evaluations filtered by optional time period and team.
        Delegates filtering to Evaluation.matches().
        """
        return [e for e in self._evaluations if e.matches(start, end, team_id)]

    def average_grade(
        self,
        team_id: ids.TeamId,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> float | None:
        """
        Calculate the average grade for evaluations
        in the given period and team.
        Returns None if there are no matching evaluations.
        """
        filtered = self.get_evaluations(
            start=start, end=end, team_id=team_id
        )
        if not filtered:
            return None
        total = sum(e.grade for e in filtered)
        average = total / len(filtered)
        return round(average, 2)


class Task(Entity):

    def __init__(
        self,
        id: ids.TaskId,
        team_id: ids.TeamId,
        supervisor_id: ids.UserId,
        executor_id: ids.UserId,
        status: task_status.TaskStatus,
    ):
        self._id = id
        self._team_id = team_id
        self._supervisor_id = supervisor_id
        self._executor_id = executor_id
        self._status = status

    @property
    def id(self) -> ids.TaskId:
        return self._id

    @property
    def team_id(self) -> ids.TeamId:
        return self._team_id

    @property
    def supervisor_id(self) -> ids.UserId:
        return self._supervisor_id

    @property
    def executor_id(self) -> ids.UserId:
        return self._executor_id

    @property
    def status(self) -> task_status.TaskStatus:
        return self._status

    def create_evaluation(self, grade: grade.Grade) -> Evaluation:
        """Set Evaluation if status is done"""

        if self._status != task_status.TaskStatus.DONE:
            raise custom_exception.EvaluationException(
                "Task status is not done"
            )

        return Evaluation(
            self._executor_id, self._team_id, self._id,
            grade, datetime.now(timezone.utc)
        )
