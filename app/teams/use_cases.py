from app.teams.unit_of_work import TeamSQLAlchemyUnitOfWork
from app.teams.custom_exception import UserNotFoundException
from app.teams import (
    dto,
    models,
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
        user = await self.uow.repos.user.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundException(
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


