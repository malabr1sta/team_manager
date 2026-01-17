from abc import ABC, abstractmethod

from app.teams.models import Member, Team
from app.teams import custom_exception
from app.core.custom_types import ids, role


def create_team(user_id: ids.UserId, team_id: ids.TeamId ) -> Team:
    """Funtions for create team"""
    admin = Member(user_id, team_id, role.UserRole.ADMIN)
    return Team(team_id, [admin])


class TeamManagement(ABC):
    """Base class for team management actions requiring admin access."""

    def __init__(self, team: Team, admin_id: ids.UserId):
        """Initialize management context and validate admin permissions."""
        if not team.is_admin(admin_id):
            raise custom_exception.MemberNotAdminException(
                "Member is not at team admin"
            )
        self._team = team
        self._admin_id = admin_id

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute a management action with arbitrary arguments."""
        raise NotImplementedError


class ActionAddMemberTeam(TeamManagement):
    """Add a new member to the team."""

    def execute(self, user_id: ids.UserId, role: role.UserRole):
        self._team.add_member(
            user_id, role
        )


class ActionRemoveMemberTeam(TeamManagement):
    """Remove an existing member from the team."""

    def execute(self, user_id: ids.UserId, role: role.UserRole):
        self._team.remove_member(user_id, role)


class ActionAssigningRolesTeam(TeamManagement):
    "Assigning roles in team"

    def execute(
            self, user_id: ids.UserId, old_role: role.UserRole,
            new_role: role.UserRole
    ):
        self._team.change_role(user_id, old_role, new_role)
