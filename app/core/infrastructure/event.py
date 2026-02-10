from typing import Type, TypeVar, Generic
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class DomainEvent(ABC):
    """Protocol for all domain events."""
    pass


TEvent = TypeVar('TEvent', bound=DomainEvent)


class EventHandler(ABC, Generic[TEvent]):
    """Protocol for event handlers."""

    @abstractmethod
    async def handle(self, event: TEvent, session: AsyncSession) -> None:
        """Handle domain event."""
        ...


class EventBus(ABC):
    """Protocol for event bus."""

    @abstractmethod
    async def publish(self, event: DomainEvent, session: AsyncSession) -> None:
        """Publish event to all subscribers."""
        ...

    @abstractmethod
    async def subscribe(
        self,
        event_type: Type[TEvent],
        handler: EventHandler[TEvent]
    ) -> None:
        """Subscribe handler to event type."""
        ...
