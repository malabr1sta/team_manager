from fastapi import HTTPException

from app.core.custom_types import ids
from app.scheduling import custom_exception, dto, management
from app.scheduling.models import Meeting
from app.scheduling.unit_of_work import SchedulingSQLAlchemyUnitOfWork


def map_scheduling_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, custom_exception.MeetingsManagerException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.MeetingsMemberException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.MeetingOverlapError):
        return HTTPException(409, str(exc))
    if isinstance(exc, custom_exception.MeetingCancelledError):
        return HTTPException(400, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(400, str(exc))
    if isinstance(exc, HTTPException):
        return exc
    return HTTPException(400, str(exc))


def _to_meeting_dto(meeting: Meeting) -> dto.MeetingReadDTO:
    if meeting.id is None:
        raise HTTPException(400, "Meeting id is missing")
    participants = []
    for participant in meeting.participants:
        if participant is None or participant.meeting_id is None:
            continue
        participants.append(
            dto.MeetingParticipantReadDTO(
                user_id=participant.user_id,
                meeting_id=participant.meeting_id,
            )
        )
    return dto.MeetingReadDTO(
        id=meeting.id,
        organizer_id=meeting.organizer_id,
        team_id=meeting.team_id,
        start=meeting.start,
        end=meeting.end,
        description=meeting.description,
        is_cancelled=meeting.is_cancelled,
        participants=participants,
    )


class CreateMeetingUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.CreateMeetingCommand) -> dto.MeetingReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        team = await self.uow.repos.team.get_by_id(command.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        meeting = management.create_meeting(
            user_id=ids.UserId(command.actor_user_id),
            team=team,
            meeting_id=ids.MeetingId(0),
            start=command.start,
            end=command.end,
            description=command.description,
        )
        await self.uow.repos.meeting.save(meeting)
        await self.uow.commit()
        return _to_meeting_dto(meeting)


class ReadMeetingUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, meeting_id: int, actor_user_id: int) -> dto.MeetingReadDTO:
        meeting = await self.uow.repos.meeting.get_by_id(meeting_id)
        if meeting is None:
            raise HTTPException(404, "Meeting not found")
        team = await self.uow.repos.team.get_by_id(meeting.team_id)
        if team is None or not team.is_member(ids.UserId(actor_user_id)):
            raise HTTPException(403, "No access to meeting")
        return _to_meeting_dto(meeting)


class ListMeetingUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
            self,
            actor_user_id: int,
            team_id: int,
            limit: int,
            offset: int,
    ) -> dto.MeetingListDTO:
        team = await self.uow.repos.team.get_by_id(team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        if not team.is_member(ids.UserId(actor_user_id)):
            raise HTTPException(403, "No access to team meetings")
        meetings = await self.uow.repos.meeting.get_by_team(team_id)
        items = [_to_meeting_dto(meeting) for meeting in meetings]
        paged_items = items[offset: offset + limit]
        return dto.MeetingListDTO(
            items=paged_items,
            total=len(items),
            limit=limit,
            offset=offset,
        )


class AddParticipantUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
            self,
            meeting_id: int,
            target_user_id: int,
            actor_user_id: int,
    ) -> dto.MeetingReadDTO:
        meeting = await self.uow.repos.meeting.get_by_id(meeting_id)
        if meeting is None:
            raise HTTPException(404, "Meeting not found")
        previous_participant_ids = [
            int(item.user_id) for item in meeting.participants if item is not None
        ]
        team = await self.uow.repos.team.get_by_id(meeting.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        user = await self.uow.repos.user.get_by_id(target_user_id)
        if user is None:
            raise HTTPException(404, "User not found")
        action = management.ActionAddMeeting(
            user_id=ids.UserId(actor_user_id),
            meeting=meeting,
        )
        action.execute(user=user, team=team)
        meeting.mark_updated_event(previous_participant_ids)
        await self.uow.repos.meeting.save(meeting)
        await self.uow.commit()
        return _to_meeting_dto(meeting)


class RemoveParticipantUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
            self,
            meeting_id: int,
            target_user_id: int,
            actor_user_id: int,
    ) -> dto.MeetingReadDTO:
        meeting = await self.uow.repos.meeting.get_by_id(meeting_id)
        if meeting is None:
            raise HTTPException(404, "Meeting not found")
        previous_participant_ids = [
            int(item.user_id) for item in meeting.participants if item is not None
        ]
        action = management.ActionRemoveMeeting(
            user_id=ids.UserId(actor_user_id),
            meeting=meeting,
        )
        action.execute(ids.UserId(target_user_id))
        meeting.mark_updated_event(previous_participant_ids)
        await self.uow.repos.meeting.save(meeting)
        await self.uow.commit()
        return _to_meeting_dto(meeting)


class CancelMeetingUseCase:
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
            self, meeting_id: int, actor_user_id: int
    ) -> dto.MeetingReadDTO:
        meeting = await self.uow.repos.meeting.get_by_id(meeting_id)
        if meeting is None:
            raise HTTPException(404, "Meeting not found")
        action = management.ActionCancelMeeting(
            user_id=ids.UserId(actor_user_id),
            meeting=meeting,
        )
        action.execute()
        meeting.mark_cancelled_event()
        await self.uow.repos.meeting.save(meeting)
        await self.uow.commit()
        return _to_meeting_dto(meeting)
