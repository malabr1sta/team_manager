from fastapi import APIRouter, status

from app.deps.user import (
    UserDepend
)
from app.deps.team import (
    TeamUoW
)
from app.teams import dto, use_cases


teams_router = APIRouter(
    prefix="/teams",
    tags=["teams"],
)


@teams_router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(
        command_body: dto.CreateTeamCommand,
        user: UserDepend,
        uow: TeamUoW
):
    command = command_body.model_copy(update={"user_id": user.id})
    return await use_cases.CreateTeamUseCase(uow).execute(command)


@teams_router.get("/{team_id}")
async def get_team(
        team_id: int,
        user: UserDepend,
        uow: TeamUoW
):
    command = dto.TeamReadResponsDTO(user_id=user.id, team_id=team_id)
    return await use_cases.ReadTeamUseCase(uow).execute(command)

