from app.core.entity import Entity
from app.core.custom_types import ids

from abc import ABC


class BaseUser(Entity, ABC):

    def __init__(self, id: ids.UserId, username: str = ""):
        self.id = id
        self.username = username
