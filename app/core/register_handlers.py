from app.core.shared.events import teams as team_event
from app.core.custom_types import session_factory
from app.core.infrastructure.event import EventHandler, EventBus
from app.tasks import (
    repository as tasks_repo,
    handlers as tasks_handlers
)


async def register_event_handlers(
        bus: EventBus,
        session_factory: session_factory.AsyncSessionFactory
):
    """
    Register all domain event handlers to the given EventBus.

    Each event type can have one or more handlers. Handlers receive
    a session factory to interact with the database asynchronously.

    Args:
        EventBus: The event bus instance where handlers will be subscribed.
        session_factory (AsyncSessionFactory): A callable that returns an
            async context manager yielding an AsyncSession.

    Usage:
        await register_event_handlers(app.state.bus, app.state.async_session)
    """
    handlers_map = {
        team_event.TeamCreated: [
            tasks_handlers.TeamCreatedHandler(
                tasks_repo.SQLAlchemyTeamRepository, session_factory
            ),
        ],
    }

    for event_type, handlers in handlers_map.items():
        for handler in handlers:
            await bus.subscribe(event_type, handler)
