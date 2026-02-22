from sqlalchemy import select

from app.core.repositories.base import AbstractRepository
from app.core.custom_types import ids
from app.teams import (
    models,
    orm_models,
    mappers
)

class SQLAlchemyUserRepository(AbstractRepository[models.User]):
    """Implementing a user's repository"""

    async def get_by_id(self, id: int) -> models.User | None:
        result = await self.session.execute(
            select(orm_models.TeamUserOrm)
            .where(orm_models.TeamUserOrm.id == id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            return None
        return mappers.UserMapper.to_domain(orm)

    async def save(self, domain: models.User):
        self.session.add(
            orm_models.TeamUserOrm(id=domain.id)
        )


class SQLAlchemyMemberRepository(AbstractRepository[models.Member]):
    """Implementing a member's repository"""

    async def get_by_user(self, user_id: int) -> list[models.Member]:
        result = await self.session.execute(
            select(orm_models.MemberOrm)
            .where(orm_models.MemberOrm.user_id == user_id)
        )
        orms = result.scalars().all()
        return [
            mappers.MemberMapper.to_domain(orm_model)
            for orm_model in orms
        ]

    async def get_by_user_and_team(
        self, user_id: int, team_id: int | None
    ) -> models.Member | None:
        result = await self.session.execute(
            select(orm_models.MemberOrm)
            .where(
                orm_models.MemberOrm.user_id == user_id,
                orm_models.MemberOrm.team_id == team_id
            )
        )
        orm_model = result.scalar_one_or_none()
        return mappers.MemberMapper.to_domain(orm_model) if orm_model else None

    async def save(self, domain: models.Member):
        result = await self.session.execute(
            select(orm_models.MemberOrm)
            .where(
                orm_models.MemberOrm.user_id == domain.user_id,
                orm_models.MemberOrm.team_id == domain.team_id
            )
        )
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            orm_member = mappers.MemberMapper.to_orm(domain)
            self.session.add(orm_member)
        else:
            mappers.MemberMapper.update_orm(orm_model, domain)



class SQLAlchemyTeamRepository(AbstractRepository[models.Team]):
    """Implementing a team's repository"""

    async def get_by_id(self, team_id: int) -> models.Team | None:
        result = await self.session.execute(
            select(orm_models.TeamOrm)
            .where(orm_models.TeamOrm.id == team_id)
        )
        orm_model = result.scalar_one_or_none()
        return mappers.TeamMapper.to_domain(orm_model) if orm_model else None

    async def save(self, domain: models.Team):
        if domain.id is None:
            orm_team = mappers.TeamMapper.to_orm(domain)
            self.session.add(orm_team)
            await self.session.flush()
            domain._id = ids.TeamId(orm_team.id)
        else:
            result = await self.session.execute(
                select(orm_models.TeamOrm)
                .where(orm_models.TeamOrm.id == domain.id)
            )
            orm_model = result.scalar_one()
            mappers.TeamMapper.update_orm(orm_model, domain)
        self.uow._seen.add(domain)
