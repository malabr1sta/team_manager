from typing import Protocol, runtime_checkable

from app.identity.models import User


@runtime_checkable
class IdentityUserProtocol(Protocol):
    """Protocol user's repository"""

    async def get_by_id(self, user_id: int) -> User | None:
        ...

    async def get_by_email(self, email: str) -> User | None:
        ...

    async def save(self, domain: User) -> None:
        ...


@runtime_checkable
class IdentityRepos(Protocol):
    user: IdentityUserProtocol
