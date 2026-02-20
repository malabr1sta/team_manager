from dataclasses import dataclass
from app.core.custom_types import ids, role
from app.core.entity import Entity
from app.core.aggregate import AggregateRoot
from app.teams import custom_exception

from app.core.shared.events import teams as team_event


@dataclass(frozen=True)
class User:
    """User teams domain."""
    id: ids.UserId


@dataclass(frozen=True)
class Member:
    """Represents a team member with an assigned role."""
    user_id: ids.UserId
    team_id: ids.TeamId | None
    role: role.UserRole


class Team(Entity, AggregateRoot):
    """Team aggregate root."""

    def __init__(
            self, id: ids.TeamId | None = None,
            members: list[Member] | None = None,
            name: str = ""
    ):
        """Create a team with a unique identifier."""
        AggregateRoot.__init__(self)
        self._id = id
        self._members = members if members is not None else []
        self._name = name
        self.__user_create_id: ids.UserId | None = None

    @property
    def user_create_id(self) -> ids.UserId | None:
        return self.__user_create_id

    @user_create_id.setter
    def user_create_id(self, value: ids.UserId):
        self.__user_create_id = value

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
            self, user_id: ids.UserId, role_member: role.UserRole
    ) -> Member | None:
        """Add member in team"""
        if self.id is None:
            raise custom_exception.TeamIdMissingException(
                "Cannot add member to a team without id")
        new_member = Member(user_id, self._id, role_member)
        if new_member not in self._members:
            self._members.append(new_member)
            if role_member != role.UserRole.ADMIN:
                event = team_event.MemberAddTeam(
                    team_id=self.id,
                    user_id=new_member.user_id,
                    role=new_member.role
                )
                self.record_event(event)

            return new_member

    def remove_member(
            self, user_id: ids.UserId, role_member: role.UserRole
    ) -> Member:
        """Remove member in team"""
        member = self.get_member(user_id, role_member)
        self._members.remove(member)
        if member.team_id is not None and role_member != role.UserRole.ADMIN:
            event = team_event.MemberRemoveTeam(
                team_id=member.team_id,
                user_id=member.user_id,
                role=member.role
            )
            self.record_event(event)

        return member

    def has_member(self, user_id: ids.UserId, role: role.UserRole) -> bool:
            """Check whether the user is already a team member."""
            return Member(user_id, self.id, role) in self.members

    def change_role(
        self,
        user_id: ids.UserId,
        old_role: role.UserRole,
        new_role: role.UserRole,
    ) -> None:
        """Change member role in team."""
        if old_role == new_role:
            return

        old_member = Member(user_id, self.id, old_role)
        new_member = Member(user_id, self.id, new_role)

        self._validate_role_change(old_member)
        self._apply_role_change(old_member, new_member)
        self._record_role_change_event(old_member, new_member)


    def _validate_role_change(self, old_member: Member) -> None:
        if old_member not in self._members:
            raise custom_exception.MemberNotFoundException(
                "User with this role not found"
            )

    def _apply_role_change(
            self, old_member: Member, new_member: Member
    ) -> None:
        """Replace old member entry with new one,
        or just remove if duplicate exists."""
        if new_member in self._members:
            self._members.remove(old_member)
            return

        index = self._members.index(old_member)
        self._members[index] = new_member

    def _record_role_change_event(
            self, old_member: Member, new_member: Member
    ) -> None:
        if new_member.team_id is None:
            return

        event = self._build_role_change_event(old_member, new_member)
        self.record_event(event)

    def _build_role_change_event(
        self,
        old_member: Member,
        new_member: Member,
    ) -> team_event.MemberEvent:

        if self.id is None:
            raise ValueError("Cannot record event for a team without an id")

        if new_member.role == role.UserRole.ADMIN:
            return team_event.MemberRemoveTeam(
                team_id=self.id,
                user_id=old_member.user_id,
                role=old_member.role,
            )

        if old_member.role == role.UserRole.ADMIN:
            return team_event.MemberAddTeam(
                team_id=self.id,
                user_id=new_member.user_id,
                role=new_member.role,
            )

        return team_event.MemberChangeRole(
            team_id=self.id,
            user_id=new_member.user_id,
            new_role=new_member.role,
            old_role=old_member.role,
        )
