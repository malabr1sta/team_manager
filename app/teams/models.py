from dataclasses import dataclass
from app.core.custom_types import ids, role
from app.core.entity import Entity
from app.teams import custom_exception


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
            members: list[Member] | None = None,
            name: str = ""
    ):
        """Create a team with a unique identifier."""
        self._id = id
        self._members = members if members is not None else []
        self._name = name

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
        for member in self.members:
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

    def is_member(self, user_id: ids.UserId) -> bool:
        """Check whether the given user is a team member."""
        return any(
            member.user_id == user_id
            for member in self._members
        )

    def add_member(
            self, user_id: ids.UserId, role: role.UserRole
    ) -> Member | None:
        """Add member in team"""
        if self.id is None:
            raise custom_exception.TeamIdMissingException(
                "Cannot add member to a team without id")
        new_member = Member(user_id, self._id, role)
        if new_member not in self._members:
            self._members.append(new_member)
            return new_member

    def remove_member(
            self, user_id: ids.UserId, role: role.UserRole
    ) -> Member:
        """Remove member in team"""
        member = self.get_member(user_id, role)
        self._members.remove(member)
        return member

    def has_member(self, user_id: ids.UserId, role: role.UserRole) -> bool:
            """Check whether the user is already a team member."""
            return Member(user_id, self.id, role) in self.members

    def change_role(
        self,
        user_id: ids.UserId,
        old_role: role.UserRole,
        new_role: role.UserRole,
    ):
        "Change roles in team"

        old_member = Member(user_id, self.id, old_role)
        new_member = Member(user_id, self.id, new_role)

        if old_member not in self._members:
            raise custom_exception.MemberNotFoundException(
                "User with this role not found"
            )

        if new_member in self._members:
            self._members.remove(old_member)
            return

        index = self._members.index(old_member)
        self._members[index] = new_member
