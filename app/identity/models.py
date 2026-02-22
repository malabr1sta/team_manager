from app.core.entity import Entity
from app.core.custom_types import ids
from app.core.aggregate import AggregateRoot
from app.core.shared.events import identity as identity_event
from app.identity.custom_exception import UserDeleteException



class User(Entity, AggregateRoot):
    """
    Domain user aggregate with email, username,
    deletion state, and email validation.
    """

    def __init__(
            self, id: ids.UserId,
            email: str,
            username: str | None,
            deleted: bool = False
    ):
        AggregateRoot.__init__(self)
        self.id = id
        self.email = email
        self.username = username or email
        self.deleted = deleted

    def update(
        self,
        *,
        email: str | None = None,
        username: str | None = None,
    ):
        if self.deleted:
            raise UserDeleteException("Deleted user cannot be updated")
        ## TODO
        self.email = email or self.email
        if '@' not in self.email:
            raise ValueError
        self.username = username or self.username
        self.record_event(
            identity_event.UserUpdated(
                user_id=self.id,
                username=self.username,
            )
        )

    def delete(self):
        if self.deleted:
            return
        self.deleted = True
        self.record_event(
            identity_event.UserDeleted(user_id=self.id)
        )
