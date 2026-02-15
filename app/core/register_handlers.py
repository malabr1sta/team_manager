from app.core.shared.events import teams as team_event
from app.core.infrastructure.event import EventBus
from app.tasks import (
    handlers as tasks_handlers,
    unit_of_work as tasks_uow
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def register_event_handlers(
        bus: EventBus,
        session_factory: async_sessionmaker[AsyncSession]
):
    """
    Register all domain event handlers to the given EventBus.

    Each event type can have one or more handlers. Handlers receive
    a session factory to interact with the database asynchronously.

    Args:
        EventBus: The event bus instance where handlers will be subscribed.

    Usage:
        await register_event_handlers(app.state.bus, app.state.async_session)
    """
    handlers_map = {
        team_event.TeamCreated: [

            tasks_handlers.TeamCreatedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),

            ),
        ],
    }

    for event_type, handlers in handlers_map.items():
        for handler in handlers:
            await bus.subscribe(event_type, handler)
