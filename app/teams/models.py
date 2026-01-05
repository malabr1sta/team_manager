from dataclasses import dataclass
from app.core.custom_types import ids, role
from app.core.entity import Entity
from app.teams import custom_exception

from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Member:
    """Represents a team member with an assigned role."""
    user_id: ids.UserId
    team_id: ids.TeamId | None
    role: role.UserRole


class Team(Entity):
    """Team aggregate root."""

    def __init__(
            self, id: ids.TeamId | None = None,
            members: list[Member] | None = None
    ):
        """Create a team with a unique identifier."""
        self._id = id
        self._members = members if members is not None else []

    @property
    def id(self) -> ids.TeamId | None:
        """Return team identifier."""
        return self._id

    @property
    def members(self) -> tuple[Member, ...]:
        """Return team members as an immutable collection."""
        return tuple(self._members)

    def get_member(self, user_id: ids.UserId, role: role.UserRole) -> Member:
        """Return team member by user id or raise an error if not found."""
        for member in self._members:
            if member.user_id == user_id and member.role == role:
                return member
        raise custom_exception.MemberNotFoundException(
            "User is not a team member")

    def is_admin(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team admin."""
        return any(
            member.user_id == user_id and member.role == role.UserRole.ADMIN
            for member in self._members
        )

    def has_member(self, member: Member) -> bool:
        """Check whether the user is already a team member."""
        return member in self.members


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
        if self._team.id is None:
            raise custom_exception.TeamIdMissingException(
                "Cannot add member to a team without id")
        new_member = Member(user_id, self._team.id, role)
        if not self._team.has_member(new_member):
            self._team._members.append(new_member)


class ActionRemoveMemberTeam(TeamManagement):
    """Remove an existing member from the team."""

    def execute(self, member: Member):
        if self._team.has_member(member):
            self._team._members.remove(member)



class ActionAssigningRolesTeam(TeamManagement):
    "Assigning roles in team"

    def execute(self, old_member: Member, new_role: role.UserRole):
        if self._team.has_member(old_member):
            new_member = Member(
                user_id=old_member.user_id,
                team_id=old_member.team_id,
                role=new_role
            )
            if not self._team.has_member(new_member):
                self._team._members = [
                    new_member if member == old_member else member
                    for member in self._team._members
                ]
            else:
                self._team._members.remove(old_member)

