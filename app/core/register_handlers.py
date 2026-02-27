from app.calendar import (
    handlers as calendar_handlers,
    models as calendar_models,
    unit_of_work as calendar_uow,
)
from app.core.shared.events import teams as team_event
from app.core.shared.events import identity as user_event
from app.core.shared.events import meetings as meeting_event
from app.core.shared.events import tasks as task_event
from app.core.infrastructure.event import EventBus
from app.evaluations import (
    handlers as evaluations_handlers,
    models as evaluations_models,
    unit_of_work as evaluations_uow,
)
from app.scheduling import (
    handlers as scheduling_handlers,
    models as scheduling_models,
    unit_of_work as scheduling_uow,
)
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
            evaluations_handlers.EvaluationUserCreatedHandler(
                evaluations_uow.EvaluationSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    evaluations_uow.EvaluationRepositoryProvider,
                ),
                evaluations_models.User,
            ),
            scheduling_handlers.SchedulingUserCreatedHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    scheduling_uow.SchedulingRepositoryProvider,
                ),
                scheduling_models.User,
            ),
            calendar_handlers.CalendarUserCreatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
                calendar_models.CalendarUser,
            ),

        ],

        user_event.UserUpdated: [
            teams_handlers.TeamUserUpdatedHandler(
                teams_uow.TeamSQLAlchemyUnitOfWork(
                    session_factory, bus, teams_uow.TeamRepositoryProvider
                ),
                teams_models.User,
            ),
            tasks_handlers.TaskUserUpdatedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
                tasks_handlers.TaskUser,
            ),
            evaluations_handlers.EvaluationUserUpdatedHandler(
                evaluations_uow.EvaluationSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    evaluations_uow.EvaluationRepositoryProvider,
                ),
                evaluations_models.User,
            ),
            scheduling_handlers.SchedulingUserUpdatedHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    scheduling_uow.SchedulingRepositoryProvider,
                ),
                scheduling_models.User,
            ),
            calendar_handlers.CalendarUserUpdatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
                calendar_models.CalendarUser,
            ),
        ],

        user_event.UserDeleted: [
            teams_handlers.TeamUserDeletedHandler(
                teams_uow.TeamSQLAlchemyUnitOfWork(
                    session_factory, bus, teams_uow.TeamRepositoryProvider
                ),
                teams_models.User,
            ),
            tasks_handlers.TaskUserDeletedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
                tasks_handlers.TaskUser,
            ),
            evaluations_handlers.EvaluationUserDeletedHandler(
                evaluations_uow.EvaluationSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    evaluations_uow.EvaluationRepositoryProvider,
                ),
                evaluations_models.User,
            ),
            scheduling_handlers.SchedulingUserDeletedHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    scheduling_uow.SchedulingRepositoryProvider,
                ),
                scheduling_models.User,
            ),
            calendar_handlers.CalendarUserDeletedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
                calendar_models.CalendarUser,
            ),
        ],

        team_event.TeamCreated: [

            tasks_handlers.TeamCreatedHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),
            scheduling_handlers.SchedulingTeamCreatedHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory, bus, scheduling_uow.SchedulingRepositoryProvider
                ),
            ),

        ],

        team_event.MemberAddTeam: [

            tasks_handlers.MemberAddTeamHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),
            scheduling_handlers.SchedulingMemberAddHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory, bus, scheduling_uow.SchedulingRepositoryProvider
                ),
            ),

        ],

        team_event.MemberRemoveTeam: [

            tasks_handlers.MemberRemoveTeamHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),
            scheduling_handlers.SchedulingMemberRemoveHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory, bus, scheduling_uow.SchedulingRepositoryProvider
                ),
            ),

        ],

        team_event.MemberChangeRole: [

            tasks_handlers.MemberChangeRoleHandler(
                tasks_uow.TaskSQLAlchemyUnitOfWork(
                    session_factory, bus, tasks_uow.TaskRepositoryProvider
                ),
            ),
            scheduling_handlers.SchedulingMemberChangeRoleHandler(
                scheduling_uow.SchedulingSQLAlchemyUnitOfWork(
                    session_factory, bus, scheduling_uow.SchedulingRepositoryProvider
                ),
            ),

        ],

        task_event.TaskCreated: [
            evaluations_handlers.EvaluationTaskCreatedHandler(
                evaluations_uow.EvaluationSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    evaluations_uow.EvaluationRepositoryProvider,
                ),
            ),
            calendar_handlers.CalendarTaskCreatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
            ),
        ],

        task_event.TaskUpdated: [
            evaluations_handlers.EvaluationTaskUpdatedHandler(
                evaluations_uow.EvaluationSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    evaluations_uow.EvaluationRepositoryProvider,
                ),
            ),
            calendar_handlers.CalendarTaskUpdatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
            ),
        ],

        meeting_event.MeetingCreated: [
            calendar_handlers.CalendarMeetingCreatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
            ),
        ],

        meeting_event.MeetingUpdated: [
            calendar_handlers.CalendarMeetingUpdatedHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
            ),
        ],

        meeting_event.MeetingCancelled: [
            calendar_handlers.CalendarMeetingCancelledHandler(
                calendar_uow.CalendarSQLAlchemyUnitOfWork(
                    session_factory,
                    bus,
                    calendar_uow.CalendarRepositoryProvider,
                ),
            ),
        ],


    }

    for event_type, handlers in handlers_map.items():
        for handler in handlers:
            await bus.subscribe(event_type, handler)
