from fastapi import HTTPException

from app.teams import custom_exception
from app.teams import (
    dto,
    management
)
from app.core.custom_types import ids, role
from app.core.uow.teams import TeamUnitOfWork


class CreateTeamUseCase:
    """
    Use case for creating a new team.

    Business rules:
    - Creator automatically becomes an admin
    - Team gets unique identifier
    - TeamCreated event is recorded and published
    """

    def __init__(self, uow: TeamUnitOfWork):
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

    def __init__(self, uow: TeamUnitOfWork):
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
    def __init__(self, uow: TeamUnitOfWork):
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
    def __init__(self, uow: TeamUnitOfWork):
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
    def __init__(self, uow: TeamUnitOfWork):
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
    def __init__(self, uow: TeamUnitOfWork):
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


class TeamCapabilitiesUseCase:
    def __init__(self, uow: TeamUnitOfWork):
        self.uow = uow

    async def execute(self, team_id: int, user_id: int) -> dto.TeamCapabilitiesDTO:
        user = await self.uow.repos.user.get_by_id(user_id)
        if user is None:
            raise custom_exception.UserNotFoundException(f"User {user_id} not found")
        team = await self.uow.repos.team.get_by_id(team_id)
        if team is None:
            raise HTTPException(404, "Team not found")
        return _to_team_capabilities(team, user_id)


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


def _to_team_capabilities(team, user_id: int) -> dto.TeamCapabilitiesDTO:
    user_domain_id = ids.UserId(user_id)
    member_roles = sorted(
        {
            str(member.role)
            for member in team.members
            if int(member.user_id) == user_id
        }
    )
    is_member = team.is_member(user_domain_id)
    is_admin = team.is_admin(user_domain_id)
    is_manager = any(
        int(member.user_id) == user_id and member.role == role.UserRole.MANAGER
        for member in team.members
    )
    can_manage_team = is_admin
    can_manage_work = is_admin or is_manager
    return dto.TeamCapabilitiesDTO(
        team_id=int(team.id or 0),
        user_id=user_id,
        available_roles=member_roles,
        is_member=is_member,
        is_admin=is_admin,
        is_manager=is_manager,
        view_team=is_member,
        add_member=can_manage_team,
        remove_member=can_manage_team,
        change_member_role=can_manage_team,
        create_task=can_manage_work,
        assign_executor=can_manage_work,
        update_task=can_manage_work,
        add_comment=is_member,
        create_meeting=can_manage_work,
        manage_meeting_participants=can_manage_work,
        cancel_meeting=can_manage_work,
        evaluate_task=can_manage_work,
        view_calendar=is_member,
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
