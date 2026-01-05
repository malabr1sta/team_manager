from abc import ABC
from typing import Generic, TypeVar

from app.core.custom_types import ids


class Entity(ABC):
    """
    Base class for domain entities.

    Entities are compared by identity, not by their attributes.
    Each entity instance must define a unique `id`.
    """
    id = 0  # Must be set for each instance (identity of the entity)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id}>"

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash((self.__class__, self.id))
