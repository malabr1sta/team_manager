from abc import ABC, abstractmethod

from app.teams.models import Member, Team
from app.teams import custom_exception
from app.core.custom_types import ids, role
from app.core.shared.events import teams as team_event


def create_team(user_id: ids.UserId, team_id: ids.TeamId, name: str = "") -> Team:
    """Funtions for create team"""
    admin = Member(user_id, team_id, role.UserRole.ADMIN)
    return Team(team_id, [admin], name)


def make_team_created_event(team: Team) -> None:
    """
    Create TeamCreated event with correct team_id
    and append it to the team's event list.
    """
    if team.id is None:
        raise ValueError("Team ID must be set before creating TeamCreated")

    event = team_event.TeamCreated(team_id=team.id)
    team.record_event(event)


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

    def execute(
            self, user_id: ids.UserId, role: role.UserRole
    ) -> Member | None:
        return self._team.add_member(
            user_id, role
        )


class ActionRemoveMemberTeam(TeamManagement):
    """Remove an existing member from the team."""

    def execute(
            self, user_id: ids.UserId, role: role.UserRole
    ) -> Member:
        return self._team.remove_member(user_id, role)


class ActionAssigningRolesTeam(TeamManagement):
    "Assigning roles in team"

    def execute(
            self, user_id: ids.UserId, old_role: role.UserRole,
            new_role: role.UserRole
    ):
        self._team.change_role(user_id, old_role, new_role)
