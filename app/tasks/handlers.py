from app.core.shared.events import teams as team_event
from app.core.shared.handlers.users import UserCreatedHandler
from app.core.custom_types import ids, role
from app.core.infrastructure.event import EventHandler
from app.tasks.models import Team, TaskUser
from app.tasks.custom_exception import TeamNotFoundException
from app.tasks.unit_of_work import (
        TaskSQLAlchemyUnitOfWork
)


class TeamCreatedHandler(EventHandler[team_event.TeamCreated]):
    """Handler for TeamCreated event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow


    async def handle(self, event: team_event.TeamCreated) -> None:
        """Create TaskTeam when Team is created."""
        async with self.uow as uow:
            team = Team(ids.TeamId(event.team_id), [])
            await uow.repos.team.save(team)
            await uow.commit()


class TaskUserCreatedHandler(
    UserCreatedHandler[TaskSQLAlchemyUnitOfWork, type[TaskUser]]
):
    ...


class MemberAddTeamHandler(EventHandler[team_event.MemberAddTeam]):
    """Handler for MemblerAddTeam event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow

    async def handle(self, event: team_event.MemberAddTeam) -> None:
        """Add member in Team."""
        async with self.uow as uow:
            team_model = await uow.repos.team.get_by_id(event.team_id)
            if team_model is None:
                raise TeamNotFoundException(f"Team not found")
            team_model.add_member(
                ids.UserId(event.user_id),
                role.UserTaskRole(event.role)
            )
            await uow.repos.team.save(team_model)
            await uow.commit()


class MemberRemoveTeamHandler(EventHandler[team_event.MemberRemoveTeam]):
    """Handler for MemblerRemoveTeam event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow

    async def handle(self, event: team_event.MemberRemoveTeam) -> None:
        """Remove member in Team."""
        async with self.uow as uow:
            team_model = await uow.repos.team.get_by_id(event.team_id)
            if team_model is None:

                raise TeamNotFoundException(f"Team not found")
            team_model.remove_member(
                ids.UserId(event.user_id),
                role.UserTaskRole(event.role)
            )
            await uow.repos.team.save(team_model)
            await uow.commit()


class MemberChangeRoleHandler(EventHandler[team_event.MemberChangeRole]):
    """Handler for MemberChangeRoleHandler event."""

    def __init__(
            self,
            uow: TaskSQLAlchemyUnitOfWork,
    ):
        self.uow = uow

    async def handle(self, event: team_event.MemberChangeRole) -> None:
        """Change role member in Team."""
        async with self.uow as uow:
            team_model = await uow.repos.team.get_by_id(event.team_id)
            if team_model is None:

                raise TeamNotFoundException(f"Team not found")
            team_model.change_role(
                user_id=ids.UserId(event.user_id),
                old_role=role.UserTaskRole(event.old_role),
                new_role=role.UserTaskRole(event.new_role)
            )
            await uow.repos.team.save(team_model)
            await uow.commit()
