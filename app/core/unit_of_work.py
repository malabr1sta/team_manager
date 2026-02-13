from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.infrastructure.event import EventBus
from app.core.aggregate import AggregateRoot


class AbstractUnitOfWork(ABC):
    """
    Base class for a Unit of Work.

    Tracks aggregates that have been changed and ensures that
    all changes are committed as a single transaction. After commit,
    domain events from aggregates are published.
    """
    def __init__(self):
        """Initialize the set of tracked aggregates."""
        self._seen: set[AggregateRoot] = set()

    async def commit(self) -> None:
        """Commit the transaction and publish domain events."""
        await self._commit()
        await self._publish_events()

    @abstractmethod
    async def _publish_events(self) -> None:
        """Publish domain events from tracked aggregates."""
        ...

    @abstractmethod
    async def _commit(self) -> None:
        """Commit the underlying transaction (implementation-specific)."""
        ...


class AbstractSqlRepositoryProvider(ABC):
    """Base interface for SQL repository providers."""

    @abstractmethod
    def __init__(self, session: AsyncSession, uow: AbstractUnitOfWork):
        """Initialize the provider with a session and unit of work."""
        ...


TProvider = TypeVar('TProvider', bound=AbstractSqlRepositoryProvider)


class SQLAlchemyUnitOfWork(Generic[TProvider], AbstractUnitOfWork, ABC):
    """Unit of Work implementation using SQLAlchemy async sessions."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        bus: EventBus,
        provider_cls: Type[TProvider]
    ):
        """Initialize the UoW with a session factory,
        event bus, and repo provider."""
        super().__init__()
        self._session_factory = session_factory
        self.bus = bus
        self.provider_cls = provider_cls
        self.repos: TProvider

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork[TProvider]":
        """Enter async context: create session and repositories."""
        self.session = self._session_factory()
        self.repos = self.provider_cls(self.session, self)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit async context: rollback on error and close session."""
        if exc:
            await self.session.rollback()
        await self.session.close()

    async def _publish_events(self) -> None:
        """Publish all events from seen aggregates via the event bus."""
        for aggregate in self._seen:
            for event in aggregate.pull_events():
                await self.bus.publish(event)

    async def _commit(self) -> None:
        """Commit the current session."""
        await self.session.commit()
