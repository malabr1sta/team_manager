from fastapi import HTTPException

from app.teams.unit_of_work import TeamSQLAlchemyUnitOfWork
from app.teams import custom_exception
from app.teams import (
    dto,
    management
)
from app.core.custom_types import ids, role


class CreateTeamUseCase:
    """
    Use case for creating a new team.

    Business rules:
    - Creator automatically becomes an admin
    - Team gets unique identifier
    - TeamCreated event is recorded and published
    """

    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        """Initialize with Unit of Work."""
        self.uow = uow

    async def execute(
            self,
            command: dto.CreateTeamCommand
    ) -> dto.CreateTeamResult:
        """
        Execute team creation within a transaction.

        Steps:
        1. Create team with admin member
        2. Save team (generates team_id)
        3. Record TeamCreated event
        4. Save admin member
        5. Commit transaction (publishes events)
        6. Return result
        """
        user = await self.uow.repos.user.get_by_id(
            command.user_id if command.user_id is not None else 0
        )
        if user is None:
            raise custom_exception.UserNotFoundException(
                f"User {command.user_id} not found"
            )
        team = management.create_team(
            user_id=user.id,
            team_id=None, name=command.team_name
        )

        await self.uow.repos.team.save(team)

        if team.id is None:
            raise ValueError("Team ID was not generated after save")

        management.make_team_created_event(team)
        await self.uow.commit()
        return dto.CreateTeamResult(
            team_id=int(team.id),
            team_name=team._name,
            admin_user_id=command.user_id
        )


class ReadTeamUseCase:

    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        """Initialize with Unit of Work."""
        self.uow = uow

    async def execute(
            self,
            command: dto.TeamReadResponsDTO
    ) -> dto.TeamReadDTO:
        user = await self.uow.repos.user.get_by_id(
            command.user_id if command.user_id is not None else 0

        )
        if user is None:
            raise custom_exception.UserNotFoundException(
                f"User {command.user_id} not found"
            )
        team = await self.uow.repos.team.get_by_id(
            command.team_id
        )
        if team is None:
            raise HTTPException(404, "Team not found")
        management.TeamQuery(team, ids.UserId(user.id or 0))

        return dto.TeamReadDTO(
            id=team.id or 0,
            name=team._name,
            members=[
                dto.MemberReadDTO(
                    user_id=m.user_id,
                    role=m.role,
                )
                for m in team.members
            ],
            members_count=len(team.members),
            created_at=getattr(team, 'created_at', None),
            updated_at=getattr(team, 'updated_at', None),
            is_admin=team.is_admin(ids.UserId(user.id or 0)),
            is_member=True,
        )


class AddMemberUseCase:
    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.AddMemberCommand) -> dto.TeamReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        if command.team_id is None:
            raise ValueError("team_id is required")
        team = await self.uow.repos.team.get_by_id(command.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        target_user = await self.uow.repos.user.get_by_id(command.target_user_id)
        if target_user is None:
            raise custom_exception.UserNotFoundException(
                f"User {command.target_user_id} not found"
            )
        action = management.ActionAddMemberTeam(
            team=team,
            admin_id=ids.UserId(command.actor_user_id),
        )
        action.execute(
            ids.UserId(command.target_user_id),
            role.UserRole(command.role),
        )
        await self.uow.repos.team.save(team)
        await self.uow.commit()
        return _to_team_read_dto(team, command.actor_user_id)


class RemoveMemberUseCase:
    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, command: dto.RemoveMemberCommand) -> dto.TeamReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        team = await self.uow.repos.team.get_by_id(command.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        action = management.ActionRemoveMemberTeam(
            team=team,
            admin_id=ids.UserId(command.actor_user_id),
        )
        action.execute(
            ids.UserId(command.target_user_id),
            role.UserRole(command.role),
        )
        await self.uow.repos.team.save(team)
        await self.uow.commit()
        return _to_team_read_dto(team, command.actor_user_id)


class ChangeMemberRoleUseCase:
    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(
        self,
        command: dto.ChangeMemberRoleCommand,
    ) -> dto.TeamReadDTO:
        if command.actor_user_id is None:
            raise ValueError("actor_user_id is required")
        if command.team_id is None:
            raise ValueError("team_id is required")
        if command.target_user_id is None:
            raise ValueError("target_user_id is required")
        team = await self.uow.repos.team.get_by_id(command.team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        action = management.ActionAssigningRolesTeam(
            team=team,
            admin_id=ids.UserId(command.actor_user_id),
        )
        action.execute(
            ids.UserId(command.target_user_id),
            role.UserRole(command.old_role),
            role.UserRole(command.new_role),
        )
        await self.uow.repos.team.save(team)
        await self.uow.commit()
        return _to_team_read_dto(team, command.actor_user_id)


class ListMyTeamsUseCase:
    def __init__(self, uow: TeamSQLAlchemyUnitOfWork):
        self.uow = uow

    async def execute(self, user_id: int) -> dto.TeamListDTO:
        user = await self.uow.repos.user.get_by_id(user_id)
        if user is None:
            raise custom_exception.UserNotFoundException(f"User {user_id} not found")
        members = await self.uow.repos.member.get_by_user(user_id)
        team_items: list[dto.TeamReadDTO] = []
        seen_team_ids: set[int] = set()
        for member in members:
            if member.team_id is None or int(member.team_id) in seen_team_ids:
                continue
            team = await self.uow.repos.team.get_by_id(int(member.team_id))
            if team is None:
                continue
            team_items.append(_to_team_read_dto(team, user_id))
            seen_team_ids.add(int(member.team_id))
        return dto.TeamListDTO(items=team_items, total=len(team_items))


def _to_team_read_dto(team, user_id: int) -> dto.TeamReadDTO:
    return dto.TeamReadDTO(
        id=team.id or 0,
        name=team._name,
        members=[
            dto.MemberReadDTO(user_id=member.user_id, role=member.role)
            for member in team.members
        ],
        members_count=len(team.members),
        created_at=getattr(team, "created_at", None),
        updated_at=getattr(team, "updated_at", None),
        is_admin=team.is_admin(ids.UserId(user_id)),
        is_member=team.is_member(ids.UserId(user_id)),
    )


def map_team_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, custom_exception.MemberNotAdminException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.MemberNotFoundException):
        return HTTPException(403, str(exc))
    if isinstance(exc, custom_exception.UserNotFoundException):
        return HTTPException(404, str(exc))
    if isinstance(exc, custom_exception.TeamIdMissingException):
        return HTTPException(400, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(400, str(exc))
    if isinstance(exc, HTTPException):
        return exc
    return HTTPException(400, str(exc))
