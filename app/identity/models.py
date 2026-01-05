from app.core.entity import Entity
from app.core.custom_types import ids
from app.identity.custom_exception import UserDeleteException



class User(Entity):
    """
    Domain user aggregate with email, username,
    deletion state, and email validation.
    """

    def __init__(self, id: ids.UserId, email: str, username: str | None):
        self.id = id
        self.email = email
        self.username = username or email
        self.deleted = False

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

    def delete(self):
        if self.deleted:
            return
        self.deleted = True
