from app.core.custom_types import calendar_type, ids
from app.calendar import models, orm_models


class CalendarUserMapper:
    """Maps calendar user entities."""

    @staticmethod
    def to_domain(orm: orm_models.CalendarUserOrm) -> models.CalendarUser:
        return models.CalendarUser(
            id=ids.UserId(orm.id),
            username=orm.username or "",
        )

    @staticmethod
    def to_orm(user: models.CalendarUser) -> orm_models.CalendarUserOrm:
        return orm_models.CalendarUserOrm(
            id=user.id,
            username=user.username,
        )

    @staticmethod
    def update_orm(orm: orm_models.CalendarUserOrm, user: models.CalendarUser) -> None:
        orm.username = user.username


class CalendarEventMapper:
    """Maps calendar event entities."""

    @staticmethod
    def to_domain(orm: orm_models.CalendarEventOrm) -> models.CalendarEvent:
        reference_id: ids.TaskId | ids.MeetingId
        if orm.event_type == calendar_type.CalendarEventType.TASK:
            reference_id = ids.TaskId(orm.reference_id)
        else:
            reference_id = ids.MeetingId(orm.reference_id)
        return models.CalendarEvent(
            user_id=ids.UserId(orm.user_id),
            id=ids.CalendarEventId(orm.id),
            type=orm.event_type,
            description=orm.description,
            title=orm.title,
            time=orm.time,
            reference_id=reference_id,
            cancelled=orm.cancelled,
        )

    @staticmethod
    def to_orm(event: models.CalendarEvent) -> orm_models.CalendarEventOrm:
        return orm_models.CalendarEventOrm(
            user_id=event.user_id,
            event_type=event.type,
            title=event.title,
            description=event.description,
            time=event.time,
            reference_id=event.reference_id,
            cancelled=event.cancelled,
        )

    @staticmethod
    def update_orm(
            orm: orm_models.CalendarEventOrm,
            event: models.CalendarEvent,
    ) -> None:
        orm.user_id = event.user_id
        orm.event_type = event.type
        orm.title = event.title
        orm.description = event.description
        orm.time = event.time
        orm.reference_id = event.reference_id
        orm.cancelled = event.cancelled
