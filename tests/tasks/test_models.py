from datetime import datetime, timezone, timedelta

from app.core.custom_types import ids, role, task_status
from app.tasks import models as tasks_models, management
from app.tasks.custom_exception import (
    TaskDeadlineException,
    TaskSupervisorException,
    CommentException
)

import pytest


class TestTask:

    def test_create_task(self, get_team_for_task):
        team, manager, member = get_team_for_task
        now_time = datetime.now(timezone.utc)
        deadline = now_time + timedelta(days=3)
        task = management.create_task(
            manager.user_id, team,
            deadline, "title", "description",
        )
        assert task.team_id == manager.team_id
        with pytest.raises(TaskSupervisorException):
            management.create_task(
                member.user_id, team,
                deadline, "title", "description",
            )
        new_manager = tasks_models.MemberTask(
            ids.UserId(3),
            ids.TeamId(100),
            role.UserTaskRole.MANAGER
        )
        with pytest.raises(TaskSupervisorException):
            management.create_task(
                new_manager.user_id, team,
                deadline, "title", "description",
            )
        new_deadline = now_time - timedelta(days=3)
        with pytest.raises(TaskDeadlineException):
            management.create_task(
                manager.user_id, team,
                new_deadline, "title", "description",
            )

    def test_set_executor(self, get_task):
        task, team, manager, member = get_task
        other_member = tasks_models.MemberTask(
            ids.UserId(99),
            ids.TeamId(999),
            role.UserTaskRole.MANAGER
        )
        with pytest.raises(TaskSupervisorException):
            management.ActionAppointmentExecutorTask(
                task, member.user_id
            )
        with pytest.raises(TaskSupervisorException):
            management.ActionAppointmentExecutorTask(
                task, other_member.user_id
            )
        action = management.ActionAppointmentExecutorTask(
            task, manager.user_id
        )
        with pytest.raises(TaskSupervisorException):
            management.ActionAppointmentExecutorTask(
                task, other_member.user_id
            )
        action.execute(member.user_id, team)
        assert task.executor_id == member.user_id

    def test_update_task(self, get_task):
        task, _, manager, member = get_task
        with pytest.raises(TaskSupervisorException):
            management.ActionUpdateTask(
                task, member.user_id
            )

        action = management.ActionUpdateTask(
            task, manager.user_id
        )
        action.execute(
            title="Fix bug",
            description="Fix critical production bug",
            status=task_status.TaskStatus.IN_PROGRESS,
            deleted = True
        )
        assert task.title =="Fix bug"
        assert task.description == "Fix critical production bug"
        assert task.status == task_status.TaskStatus.IN_PROGRESS
        assert task.deleted

    def test_add_comment(self, get_task):
        task, team, _, _ = get_task
        other_member = tasks_models.MemberTask(
            ids.UserId(99),
            ids.TeamId(999),
            role.UserTaskRole.MANAGER
        )
        with pytest.raises(CommentException):
            management.ActionCreateComment(
                team, other_member.user_id
            )
            action = management.ActionCreateComment(
                team, other_member.user_id
            )
            comment = action.execute(
                task.id, "text", ids.CommentId(1)
            )
            assert comment.id == ids.CommentId(1)
