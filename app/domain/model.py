from dataclasses import dataclass, field, InitVar
from typing import Generic, Optional, Set
from abc import ABC
from uuid import UUID, uuid4

from app.domain.custom_types import role, ids


@dataclass(eq=False)
class Entity(ABC):
    """
    Base class for domain entities with a unique identity.
    Equality and hash are based only on the `id` attribute.
    """

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return getattr(self, "id", None) == getattr(other, "id", None)

    def __hash__(self):
        return hash(getattr(self, "id", None))


@dataclass(eq=False)
class User(Entity):
    """Domain user aggregate with email, username,
    deletion state, and email validation."""
    id: ids.UserId = field(
        init=False, default_factory=lambda: ids.UserId(uuid4())
    )
    email: str
    username: str | None = None
    _is_deleted: bool = field(init=False, default=False)

    def __post_init__(self):
        self._change_email(self.email)

        if self.username is None:
            self.username = self.email

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def update(
        self,
        *,
        email: Optional[str] = None,
        username: Optional[str] = None,
    ):
        if self.is_deleted:
            raise RuntimeError("Deleted user cannot be updated")

        if email is not None:
            self._change_email(email)

        if username is not None:
            self.username = username

    def _change_email(self, email: str):
        if email is None or "@" not in email:
            raise ValueError("Invalid email")
        self.email = email

    def delete(self):
        if self._is_deleted:
            return
        self._is_deleted = True


@dataclass(frozen=True)
class MemberRoleTeam:
    """
    Represents a user's role within a team.
    """
    user_id: ids.UserId
    role: role.UserRole


@dataclass(eq=False)
class Team(Entity):
    """
    Represents a team with members and their roles.
    Supports adding, removing members and changing roles.
    """
    id: ids.TeamId = field(
        init=False, default_factory=lambda: ids.TeamId(uuid4())
    )

    admin_id: InitVar[ids.UserId]
    name: str
    _members: dict[ids.UserId, MemberRoleTeam] = field(default_factory=dict)

    def __post_init__(self, admin_id: ids.UserId):
        self._members[admin_id] = MemberRoleTeam(
            user_id=admin_id,
            role=role.UserRole.ADMIN
        )

    @property
    def members(self):
        return self._members

    def _check_admin(self, user_id: ids.UserId):
        user_role = self._members.get(user_id, None)
        if user_role is None or role.UserRole.ADMIN != user_role.role:
            raise PermissionError("Only admin can change team")

    def change_role(
        self,
        admin_id: ids.UserId,
        target_user: ids.UserId,
        new_role: role.UserRole,
    ):
        """Change the role of a member, only by an admin."""
        self._check_admin(admin_id)

        if target_user not in self._members:
            raise ValueError("User not in team")

        self._members[target_user] = MemberRoleTeam(
            user_id=target_user,
            role=new_role,
        )

    def add_member(
        self,
        admin_id: ids.UserId,
        user_id: ids.UserId,
        user_role: role.UserRole = role.UserRole.MEMBER
    ):
        """Add a new member with a role, only by an admin."""
        self._check_admin(admin_id)

        if user_role is None:
            user_role = role.UserRole.MEMBER

        if user_id in self._members:
            return

        self._members[user_id] = MemberRoleTeam(
            user_id=user_id,
            role=user_role
        )

    def remove_member(
        self,
        admin_id: ids.UserId,
        user_id: ids.UserId,
    ):
        """Remove a member from the team, only by an admin."""
        self._check_admin(admin_id)
        self._members.pop(user_id, None)
