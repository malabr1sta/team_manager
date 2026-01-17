from app.teams import models as team_models
from app.teams import management
from app.teams.custom_exception import (
    MemberNotFoundException,
    MemberNotAdminException,
    TeamIdMissingException,
)
from app.core.custom_types import ids, role

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
        new_team = management.create_team(admin_id, team_id)
        assert len(new_team.members) == 1
        assert new_team.has_member(member.user_id, member.role)
        assert new_team.is_admin(admin_id)
        assert new_team.get_member(admin_id, role.UserRole.ADMIN) == member


class TestActionAdmin:

    def test_add_member(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = management.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 2
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 2

    def test_remove_member(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = management.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        action_remove = management.ActionRemoveMemberTeam(
            team, admin.user_id
        )
        action_remove.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 1

    def test_assigning_roles(self, get_team_admin, new_member):
        team, admin = get_team_admin
        action_add = management.ActionAddMemberTeam(
            team, admin.user_id
        )
        action_add.execute(new_member.user_id, new_member.role)
        action_assigning = management.ActionAssigningRolesTeam(
            team, admin.user_id
        )
        action_assigning.execute(
            new_member.user_id, new_member.role, role.UserRole.MANAGER
        )
        assert team.get_member(new_member.user_id, role.UserRole.MANAGER)
        assert not team.has_member(new_member.user_id, new_member.role)
        action_add.execute(new_member.user_id, new_member.role)
        assert len(team.members) == 3
        assert team.has_member(new_member.user_id, new_member.role)
        action_assigning.execute(
            new_member.user_id, new_member.role, role.UserRole.ADMIN
        )
        assert len(team.members) == 3
        action_assigning.execute(
            new_member.user_id, role.UserRole.ADMIN,
            role.UserRole.MANAGER
        )
        assert len(team.members) == 2


class TestException:

    def test_perm_exception(self, get_team_admin, new_member):
        team, admin = get_team_admin
        with pytest.raises(MemberNotAdminException):
            action_add = management.ActionAddMemberTeam(
                team, new_member.user_id
            )
        new_admin_member = team_models.Member(
            ids.UserId(3),
            new_member.team_id,
            role.UserRole.ADMIN
        )
        with pytest.raises(MemberNotAdminException):
            action_add = management.ActionAddMemberTeam(
                team, new_admin_member.user_id
            )
        action_add = management.ActionAddMemberTeam(
            team, admin.user_id
        )

        action_add.execute(new_member.user_id, new_member.role)
        with pytest.raises(MemberNotAdminException):
            action_add = management.ActionAddMemberTeam(
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
        action_add = management.ActionAddMemberTeam(
                team, admin.user_id
        )
        with pytest.raises(TeamIdMissingException):
            action_add.execute(new_member.user_id, new_member.role)
