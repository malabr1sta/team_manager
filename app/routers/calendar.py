from datetime import date

from fastapi import APIRouter, Query

from app.calendar import use_cases
from app.deps.calendar import CalendarUoW
from app.deps.user import UserDepend


calendar_router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
)


@calendar_router.get("/day")
async def events_for_day(
    user: UserDepend,
    uow: CalendarUoW,
    day: date = Query(...),
):
    return await use_cases.CalendarEventsForDayUseCase(uow).execute(
        user_id=user.id,
        day=day,
    )


@calendar_router.get("/month")
async def events_for_month(
    user: UserDepend,
    uow: CalendarUoW,
    year: int = Query(..., ge=1970, le=3000),
    month: int = Query(..., ge=1, le=12),
):
    return await use_cases.CalendarEventsForMonthUseCase(uow).execute(
        user_id=user.id,
        year=year,
        month=month,
    )
