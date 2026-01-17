from typing import Protocol

from app.core.custom_types import ids, role


class TeamInterface(Protocol):
    id: ids.TeamId | None

    def has_member(self, user_id: ids.UserId, role: role.UserRole) -> bool:
        ...

    def is_member(self, user_id: ids.UserId) -> bool:
        ...





