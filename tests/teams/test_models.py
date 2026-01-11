from datetime import datetime, timezone, timedelta
from app.teams import models as team_models
from app.teams.custom_exception import (
    MemberNotFoundException,
    MemberNotAdminException,
    TeamIdMissingException,
    TaskDeadlineException,
    TaskSupervisorException,
    CommentException
)
from app.core.custom_types import ids, role, task_status

import pytest


class TestTeam:

    def test_team_create(self):
        admin_id = ids.UserId(1)
        team_id = ids.TeamId(1)
        member = team_models.Member(
            admin_id,
            team_id,
            role.UserRole.ADMIN
        )
        new_team = team_models.create_team(admin_id, team_id)
        assert len(new_team.members) == 1
        assert new_team.has_member(member)
        assert new_team.is_admin(admin_id)
        assert new_team.get_member(admin_id, role.UserRole.ADMIN) == member


class TestActionAdmin:

    def test_add_member(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = team_models.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 2
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 2

    def test_remove_member(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = team_models.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        action_remove = team_models.ActionRemoveMemberTeam(
            team, admin.user_id
        )
        action_remove.execute(new_member)
        assert len(team.members) == 1
        action_remove.execute(new_member)
        assert len(team.members) == 1

    def test_assigning_uoles(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = team_models.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        action_assigning = team_models.ActionAssigningRolesTeam(
            team, admin.user_id
        )
        action_assigning.execute(new_member, role.UserRole.MANAGER)
        assert team.get_member(new_member.user_id, role.UserRole.MANAGER)
        assert not team.has_member(new_member)
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 3
        assert team.has_member(new_member)
        action_assigning.execute(new_member, role.UserRole.ADMIN)
        assert len(team.members) == 3
        action_assigning.execute(new_member, role.UserRole.MANAGER)
        assert len(team.members) == 3
        new_member_role = team_models.Member(
            new_member.user_id,
            new_member.team_id,
            role.UserRole.ADMIN
        )
        action_assigning.execute(new_member_role, role.UserRole.MANAGER)
        assert len(team.members) == 2


class TestException:

    def test_perm_exception(self, get_team_admin, new_member):
        team, admin = get_team_admin
        with pytest.raises(MemberNotAdminException):
            action_add = team_models.ActionAddMemberTeam(
                team, new_member.user_id
            )
        new_admin_member = team_models.Member(
            ids.UserId(3),
            new_member.team_id,
            role.UserRole.ADMIN
        )
        with pytest.raises(MemberNotAdminException):
            action_add = team_models.ActionAddMemberTeam(
                team, new_admin_member.user_id
            )
        action_add = team_models.ActionAddMemberTeam(
            team, admin.user_id
        )

        action_add.execute(new_member.user_id, new_member.role)
        with pytest.raises(MemberNotAdminException):
            action_add = team_models.ActionAddMemberTeam(
                team, new_member.user_id
            )

    def test_get_member_exception(self, get_team_admin, new_member):
        team, _ = get_team_admin
        with pytest.raises(MemberNotFoundException):
            team.get_member(new_member.user_id, new_member.role)

    def test_add_member_exception(self, new_member):
        admin = team_models.Member(
            ids.UserId(1), ids.TeamId(1), role.UserRole.ADMIN
        )
        team = team_models.Team(None, [admin])
        action_add = team_models.ActionAddMemberTeam(
                team, admin.user_id
        )
        with pytest.raises(TeamIdMissingException):
            action_add.execute(new_member.user_id, new_member.role)


class TestTask:

    def test_create_task(self, get_team_for_task):
        team, manager, member = get_team_for_task
        now_time = datetime.now(timezone.utc)
        deadline = now_time + timedelta(days=3)
        task = team_models.create_task(
            manager.user_id, team,
            deadline, "title", "description",
        )
        assert task.team_id == manager.team_id
        with pytest.raises(MemberNotFoundException):
            team_models.create_task(
                member.user_id, team,
                deadline, "title", "description",
            )
        new_manager = team_models.Member(
            ids.UserId(3),
            ids.TeamId(100),
            role.UserRole.MANAGER
        )
        with pytest.raises(MemberNotFoundException):
            team_models.create_task(
                new_manager.user_id, team,
                deadline, "title", "description",
            )
        new_deadline = now_time - timedelta(days=3)
        with pytest.raises(TaskDeadlineException):
            team_models.create_task(
                manager.user_id, team,
                new_deadline, "title", "description",
            )

    def test_appointment_of_an_executor(self, get_task):
        task, team, manager, member = get_task
        other_member = team_models.Member(
            ids.UserId(99),
            ids.TeamId(999),
            role.UserRole.MANAGER
        )
        with pytest.raises(TaskSupervisorException):
            team_models.ActionAppointmentExecutorTask(
                task, member.user_id
            )
        with pytest.raises(TaskSupervisorException):
            team_models.ActionAppointmentExecutorTask(
                task, other_member.user_id
            )
        action = team_models.ActionAppointmentExecutorTask(
            task, manager.user_id
        )
        action.execute(member.user_id, team)
        assert task.executor_id == member.user_id

    def test_update_task(self, get_task):
        task, team, manager, member = get_task
        with pytest.raises(TaskSupervisorException):
            team_models.ActionUpdateTask(
                task, member.user_id
            )

        action = team_models.ActionUpdateTask(
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
        task, team, manager, member = get_task
        other_member = team_models.Member(
            ids.UserId(99),
            ids.TeamId(999),
            role.UserRole.MANAGER
        )
        with pytest.raises(CommentException):
            team_models.ActionCreateComment(
                team, other_member.user_id
            )
            action = team_models.ActionCreateComment(
                team, other_member.user_id
            )
            comment = action.execute(
                task.id, "text", ids.CommentId(1)
            )
            assert comment.id == ids.CommentId(1)


























