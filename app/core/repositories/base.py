from sqlalchemy.ext.asyncio import AsyncSession
from app.core.unit_of_work import AbstractUnitOfWork
from typing import Generic, TypeVar

from abc import ABC, abstractmethod


DomainModel = TypeVar("DomainModel")


class AbstractRepository(ABC, Generic[DomainModel]):
    """Abstract repository"""

    def __init__(
            self, session: AsyncSession,
            uow: AbstractUnitOfWork
    ):
        self.session = session
        self.uow = uow

    @abstractmethod
    async def save(self, domain: DomainModel) -> None:
        ...


