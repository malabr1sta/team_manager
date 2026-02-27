from app.core.custom_types import ids, role
from app.core.infrastructure.event import EventHandler
from app.core.shared.events import teams as team_event
from app.core.shared.handlers.users import (
    UserCreatedHandler,
    UserDeletedHandler,
    UserUpdatedHandler,
)
from app.scheduling.models import Team, User
from app.scheduling.unit_of_work import SchedulingSQLAlchemyUnitOfWork


def _is_manager_role(user_role: str) -> bool:
    return user_role == role.UserRole.MANAGER


class SchedulingUserCreatedHandler(
    UserCreatedHandler[SchedulingSQLAlchemyUnitOfWork, type[User]]
):
    ...


class SchedulingUserUpdatedHandler(
    UserUpdatedHandler[SchedulingSQLAlchemyUnitOfWork, type[User]]
):
    ...


class SchedulingUserDeletedHandler(
    UserDeletedHandler[SchedulingSQLAlchemyUnitOfWork, type[User]]
):
    ...


class SchedulingTeamCreatedHandler(EventHandler[team_event.TeamCreated]):
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: team_event.TeamCreated) -> None:
        async with self.uow as uow:
            team = Team(id=ids.TeamId(event.team_id), members=[])
            await uow.repos.team.save(team)
            await uow.commit()


class SchedulingMemberAddHandler(EventHandler[team_event.MemberAddTeam]):
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: team_event.MemberAddTeam) -> None:
        async with self.uow as uow:
            team = await uow.repos.team.get_by_id(event.team_id)
            if team is None:
                team = Team(id=ids.TeamId(event.team_id), members=[])
            user = await uow.repos.user.get_by_id(event.user_id)
            if user is None:
                await uow.repos.user.save(
                    User(id=ids.UserId(event.user_id), username="")
                )
            team.add_member(
                user_id=ids.UserId(event.user_id),
                is_manager=_is_manager_role(event.role),
            )
            await uow.repos.team.save(team)
            await uow.commit()


class SchedulingMemberRemoveHandler(EventHandler[team_event.MemberRemoveTeam]):
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: team_event.MemberRemoveTeam) -> None:
        async with self.uow as uow:
            team = await uow.repos.team.get_by_id(event.team_id)
            if team is None:
                return
            team.remove_member(ids.UserId(event.user_id))
            await uow.repos.team.save(team)
            await uow.commit()


class SchedulingMemberChangeRoleHandler(EventHandler[team_event.MemberChangeRole]):
    def __init__(self, uow: SchedulingSQLAlchemyUnitOfWork):
        self.uow = uow

    async def handle(self, event: team_event.MemberChangeRole) -> None:
        async with self.uow as uow:
            team = await uow.repos.team.get_by_id(event.team_id)
            if team is None:
                return
            user = await uow.repos.user.get_by_id(event.user_id)
            if user is None:
                await uow.repos.user.save(
                    User(id=ids.UserId(event.user_id), username="")
                )
            team.change_member_role(
                user_id=ids.UserId(event.user_id),
                is_manager=_is_manager_role(event.new_role),
            )
            await uow.repos.team.save(team)
            await uow.commit()
