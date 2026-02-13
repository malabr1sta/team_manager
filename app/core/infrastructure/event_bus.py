from collections import defaultdict
from typing import Type

from app.core.infrastructure.event import (
    DomainEvent,
    EventHandler,
    EventBus,
    TEvent
)


class MemoryEventBus(EventBus):
    """Synchronous in-memory event bus implementation."""

    def __init__(self):
        self._handlers: dict[
            Type[DomainEvent],
            list[EventHandler]
        ] = defaultdict(list)

    async def subscribe(
        self,
        event_type: Type[TEvent],
        handler: EventHandler[TEvent]
    ) -> None:
        """Subscribe handler to event type."""
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish event to all registered handlers."""
        for handler in self._handlers[type(event)]:
            await handler.handle(event)

