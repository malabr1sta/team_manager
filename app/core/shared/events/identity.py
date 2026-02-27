from dataclasses import dataclass
from app.core.infrastructure.event import DomainEvent


class UserEvent(DomainEvent):
    pass


@dataclass(frozen=True)
class UserRegistered(UserEvent):
    """Event: User was registered in Identity context."""
    user_id: int
    username: str


@dataclass(frozen=True)
class UserUpdated(UserEvent):
    """Event: User was updated in Identity context."""
    user_id: int
    username: str


@dataclass(frozen=True)
class UserDeleted(UserEvent):
    """Event: User was soft-deleted in Identity context."""
    user_id: int


# @dataclass(frozen=True)
# class UserVerified(UserEvent):
#     """Event: User verified their email in Identity context."""
#     user_id: int
#     email: str
