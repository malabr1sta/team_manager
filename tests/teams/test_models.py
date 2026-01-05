from app.teams import models as team_models
from app.teams.custom_exception import (
    MemberNotFoundException,
    MemberNotAdminException
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















