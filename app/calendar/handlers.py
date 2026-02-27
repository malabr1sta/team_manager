from datetime import datetime, timezone

from app.calendar import models
from app.calendar.unit_of_work import CalendarSQLAlchemyUnitOfWork
from app.core.custom_types import calendar_type, ids
from app.core.infrastructure.event import EventHandler
from app.core.shared.events import meetings as meeting_event
from app.core.shared.events import tasks as task_event
from app.core.shared.handlers.users import (
    UserCreatedHandler,
    UserDeletedHandler,
    UserUpdatedHandler,
)


def _build_calendar_event(
    *,
    user_id: int,
    event_type: calendar_type.CalendarEventType,
    reference_id: int,
    title: str,
    description: str,
    time: datetime,
    cancelled: bool,
) -> models.CalendarEvent:
    return models.CalendarEvent(
        user_id=ids.UserId(user_id),
        id=ids.CalendarEventId(0),
        type=event_type,
        title=title,
        description=description,
        time=time,
        reference_id=(
            ids.TaskId(reference_id)
            if event_type == calendar_type.CalendarEventType.TASK
            else ids.MeetingId(reference_id)
        ),
        cancelled=cancelled,
    )


class CalendarUserCreatedHandler(
    UserCreatedHandler[CalendarSQLAlchemyUnitOfWork, type[models.CalendarUser]]
):
    """Creates calendar user projection."""

    ...


class CalendarUserUpdatedHandler(
    UserUpdatedHandler[CalendarSQLAlchemyUnitOfWork, type[models.CalendarUser]]
):
    """Updates calendar user projection."""

    ...


class CalendarUserDeletedHandler(
    UserDeletedHandler[CalendarSQLAlchemyUnitOfWork, type[models.CalendarUser]]
):
    """Marks calendar user projection as deleted."""

    ...


class CalendarTaskCreatedHandler(EventHandler[task_event.TaskCreated]):
    """Creates task calendar events."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: task_event.TaskCreated) -> None:
        async with self.uow as uow:
            deadline = event.deadline
            if deadline is None:
                return
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            target_user_ids = [event.supervisor_id]
            if event.executor_id is not None:
                target_user_ids.append(event.executor_id)
            for user_id in target_user_ids:
                user = await uow.repos.user.get_by_id(user_id)
                if user is None:
                    await uow.repos.user.save(
                        models.CalendarUser(
                            id=ids.UserId(user_id),
                            username="",
                        )
                    )
                calendar_event = _build_calendar_event(
                    user_id=user_id,
                    event_type=calendar_type.CalendarEventType.TASK,
                    reference_id=event.task_id,
                    title=event.title or f"Task #{event.task_id}",
                    description=event.description or "",
                    time=deadline,
                    cancelled=event.deleted,
                )
                await uow.repos.event.save(calendar_event)
            await uow.commit()


class CalendarTaskUpdatedHandler(EventHandler[task_event.TaskUpdated]):
    """Updates task calendar events."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: task_event.TaskUpdated) -> None:
        async with self.uow as uow:
            deadline = event.deadline
            if deadline is None:
                return
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)

            if (
                event.previous_executor_id is not None
                and event.executor_id != event.previous_executor_id
            ):
                previous_executor_event = await uow.repos.event.get_by_user_and_reference(
                    user_id=event.previous_executor_id,
                    event_type=calendar_type.CalendarEventType.TASK,
                    reference_id=event.task_id,
                )
                if previous_executor_event is not None:
                    previous_executor_event.mark_cancelled()
                    await uow.repos.event.save(previous_executor_event)

            target_user_ids = [event.supervisor_id]
            if event.executor_id is not None:
                target_user_ids.append(event.executor_id)
            for user_id in target_user_ids:
                user = await uow.repos.user.get_by_id(user_id)
                if user is None:
                    await uow.repos.user.save(
                        models.CalendarUser(
                            id=ids.UserId(user_id),
                            username="",
                        )
                    )
                calendar_event = _build_calendar_event(
                    user_id=user_id,
                    event_type=calendar_type.CalendarEventType.TASK,
                    reference_id=event.task_id,
                    title=event.title or f"Task #{event.task_id}",
                    description=event.description or "",
                    time=deadline,
                    cancelled=event.deleted,
                )
                await uow.repos.event.save(calendar_event)

            if event.deleted:
                events = await uow.repos.event.get_by_reference(
                    event_type=calendar_type.CalendarEventType.TASK,
                    reference_id=event.task_id,
                )
                for item in events:
                    item.mark_cancelled()
                    await uow.repos.event.save(item)
            await uow.commit()


class CalendarMeetingCreatedHandler(EventHandler[meeting_event.MeetingCreated]):
    """Creates meeting calendar events."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: meeting_event.MeetingCreated) -> None:
        async with self.uow as uow:
            for user_id in event.participant_ids:
                user = await uow.repos.user.get_by_id(user_id)
                if user is None:
                    await uow.repos.user.save(
                        models.CalendarUser(
                            id=ids.UserId(user_id),
                            username="",
                        )
                    )
                calendar_event = _build_calendar_event(
                    user_id=user_id,
                    event_type=calendar_type.CalendarEventType.MEETING,
                    reference_id=event.meeting_id,
                    title=f"Meeting #{event.meeting_id}",
                    description=event.description,
                    time=event.start,
                    cancelled=event.is_cancelled,
                )
                await uow.repos.event.save(calendar_event)
            await uow.commit()


class CalendarMeetingUpdatedHandler(EventHandler[meeting_event.MeetingUpdated]):
    """Updates meeting calendar events."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: meeting_event.MeetingUpdated) -> None:
        async with self.uow as uow:
            for previous_user_id in event.previous_participant_ids:
                if previous_user_id in event.participant_ids:
                    continue
                previous_event = await uow.repos.event.get_by_user_and_reference(
                    user_id=previous_user_id,
                    event_type=calendar_type.CalendarEventType.MEETING,
                    reference_id=event.meeting_id,
                )
                if previous_event is not None:
                    previous_event.mark_cancelled()
                    await uow.repos.event.save(previous_event)

            for user_id in event.participant_ids:
                user = await uow.repos.user.get_by_id(user_id)
                if user is None:
                    await uow.repos.user.save(
                        models.CalendarUser(
                            id=ids.UserId(user_id),
                            username="",
                        )
                    )
                calendar_event = _build_calendar_event(
                    user_id=user_id,
                    event_type=calendar_type.CalendarEventType.MEETING,
                    reference_id=event.meeting_id,
                    title=f"Meeting #{event.meeting_id}",
                    description=event.description,
                    time=event.start,
                    cancelled=event.is_cancelled,
                )
                await uow.repos.event.save(calendar_event)
            await uow.commit()


class CalendarMeetingCancelledHandler(EventHandler[meeting_event.MeetingCancelled]):
    """Cancels meeting calendar events."""

    def __init__(self, uow: CalendarSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: meeting_event.MeetingCancelled) -> None:
        async with self.uow as uow:
            for user_id in event.participant_ids:
                calendar_event = await uow.repos.event.get_by_user_and_reference(
                    user_id=user_id,
                    event_type=calendar_type.CalendarEventType.MEETING,
                    reference_id=event.meeting_id,
                )
                if calendar_event is None:
                    continue
                calendar_event.mark_cancelled()
                await uow.repos.event.save(calendar_event)
            await uow.commit()
