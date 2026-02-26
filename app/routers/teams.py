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
    try:
        return await use_cases.CreateTeamUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)


@teams_router.get("/{team_id}")
async def get_team(
        team_id: int,
        user: UserDepend,
        uow: TeamUoW
):
    command = dto.TeamReadResponsDTO(user_id=user.id, team_id=team_id)
    try:
        return await use_cases.ReadTeamUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)


@teams_router.get("")
async def list_my_teams(
        user: UserDepend,
        uow: TeamUoW
):
    try:
        return await use_cases.ListMyTeamsUseCase(uow).execute(user.id)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)


@teams_router.post("/{team_id}/members")
async def add_member(
        team_id: int,
        command_body: dto.AddMemberCommand,
        user: UserDepend,
        uow: TeamUoW
):
    command = command_body.model_copy(
        update={"team_id": team_id, "actor_user_id": user.id}
    )
    try:
        return await use_cases.AddMemberUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)


@teams_router.delete("/{team_id}/members/{member_id}")
async def remove_member(
        team_id: int,
        member_id: int,
        role: str,
        user: UserDepend,
        uow: TeamUoW
):
    command = dto.RemoveMemberCommand(
        team_id=team_id,
        actor_user_id=user.id,
        target_user_id=member_id,
        role=role,
    )
    try:
        return await use_cases.RemoveMemberUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)


@teams_router.patch("/{team_id}/members/{member_id}/role")
async def change_member_role(
        team_id: int,
        member_id: int,
        command_body: dto.ChangeMemberRoleCommand,
        user: UserDepend,
        uow: TeamUoW
):
    command = command_body.model_copy(
        update={
            "team_id": team_id,
            "actor_user_id": user.id,
            "target_user_id": member_id
        }
    )
    try:
        return await use_cases.ChangeMemberRoleUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_team_exception(exc)

