from app.core.infrastructure.event import DomainEvent


class AggregateRoot:
    """Base class for aggregate roots that record domain events."""

    def __init__(self):
        """Initialize the aggregate with an empty event list."""
        self._events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event produced by this aggregate."""
        self._events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Return and clear all recorded domain events."""
        events = self._events[:]
        self._events.clear()
        return events

