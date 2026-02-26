from app.core.shared.events import teams as team_event
from app.core.shared.events import identity as user_event
from app.core.infrastructure.event import EventBus
from app.tasks import (
    handlers as tasks_handlers,
    unit_of_work as tasks_uow
)
from app.teams import (
    handlers as teams_handlers,
    unit_of_work as teams_uow,
    models as teams_models
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

        user_event.UserRegistered: [

            teams_handlers.TeamUserCreatedHandler(
                teams_uow.TeamSQLAlchemyUnitOfWork(
                    session_factory, bus, teams_uow.TeamRepositoryProvider
                ),
                teams_models.User
            ),
            tasks_handlers.TaskUserCreatedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
                tasks_handlers.TaskUser
            ),

        ],

        team_event.TeamCreated: [

            tasks_handlers.TeamCreatedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),

        ],

        team_event.MemberAddTeam: [

            tasks_handlers.MemberAddTeamHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),

        ],

        team_event.MemberRemoveTeam: [

            tasks_handlers.MemberRemoveTeamHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),

        ],

        team_event.MemberChangeRole: [

            tasks_handlers.MemberChangeRoleHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),

        ],


    }

    for event_type, handlers in handlers_map.items():
        for handler in handlers:
            await bus.subscribe(event_type, handler)
