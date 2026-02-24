from typing import Generic, TypeVar
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import AbstractUnitOfWork


DomainModel = TypeVar("DomainModel")


class AbstractRepository(ABC, Generic[DomainModel]):
    """Abstract repository"""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @property
    def session(self) -> AsyncSession:
        """Access session through UnitOfWork."""
        return self.uow.session

    @abstractmethod
    async def save(self, domain: DomainModel) -> None:
        ...
