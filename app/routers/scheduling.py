from fastapi import APIRouter, Query, status

from app.deps.scheduling import SchedulingUoW
from app.deps.user import UserDepend
from app.scheduling import dto, use_cases


scheduling_router = APIRouter(
    prefix="/scheduling",
    tags=["scheduling"],
)


@scheduling_router.post("/meetings", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    command_body: dto.CreateMeetingCommand,
    user: UserDepend,
    uow: SchedulingUoW,
):
    command = command_body.model_copy(update={"actor_user_id": user.id})
    try:
        return await use_cases.CreateMeetingUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)


@scheduling_router.get("/meetings/{meeting_id}")
async def get_meeting(
    meeting_id: int,
    user: UserDepend,
    uow: SchedulingUoW,
):
    try:
        return await use_cases.ReadMeetingUseCase(uow).execute(meeting_id, user.id)
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)


@scheduling_router.get("/meetings")
async def list_team_meetings(
    user: UserDepend,
    uow: SchedulingUoW,
    team_id: int = Query(..., gt=0),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        return await use_cases.ListMeetingUseCase(uow).execute(
            actor_user_id=user.id,
            team_id=team_id,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)


@scheduling_router.post("/meetings/{meeting_id}/participants/{user_id}")
async def add_meeting_participant(
    meeting_id: int,
    user_id: int,
    user: UserDepend,
    uow: SchedulingUoW,
):
    try:
        return await use_cases.AddParticipantUseCase(uow).execute(
            meeting_id=meeting_id,
            target_user_id=user_id,
            actor_user_id=user.id,
        )
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)


@scheduling_router.delete("/meetings/{meeting_id}/participants/{user_id}")
async def remove_meeting_participant(
    meeting_id: int,
    user_id: int,
    user: UserDepend,
    uow: SchedulingUoW,
):
    try:
        return await use_cases.RemoveParticipantUseCase(uow).execute(
            meeting_id=meeting_id,
            target_user_id=user_id,
            actor_user_id=user.id,
        )
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)


@scheduling_router.post("/meetings/{meeting_id}/cancel")
async def cancel_meeting(
    meeting_id: int,
    user: UserDepend,
    uow: SchedulingUoW,
):
    try:
        return await use_cases.CancelMeetingUseCase(uow).execute(meeting_id, user.id)
    except Exception as exc:
        raise use_cases.map_scheduling_exception(exc)
