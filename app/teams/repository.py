from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.teams import (
    models,
    orm_models,
    mappers
)

class SQLAlchemyUserRepository:
    """Implementing a user's repository"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, id: int):
        self.session.add(
            orm_models.TeamUserOrm(id=id)
        )


class SQLAlchemyMemberRepository:
    """Implementing a member's repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def save(self, member: models.Member):
        result = await self.session.execute(
            select(orm_models.MemberOrm)
            .where(
                orm_models.MemberOrm.user_id == member.user_id,
                orm_models.MemberOrm.team_id == member.team_id
            )
        )
        orm_model = result.scalar_one_or_none()
        if orm_model is None:
            orm_member = mappers.MemberMapper.to_orm(member)
            self.session.add(orm_member)
        else:
            mappers.MemberMapper.update_orm(orm_model, member)


class SQLAlchemyTeamRepository:
    """Implementing a team's repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: int) -> models.Team | None:
        result = await self.session.execute(
            select(orm_models.TeamOrm)
            .where(orm_models.TeamOrm.id == team_id)
            .options(selectinload(orm_models.TeamOrm.members))
        )
        orm_model = result.scalar_one_or_none()
        return mappers.TeamMapper.to_domain(orm_model) if orm_model else None

    async def save(self, team: models.Team):
        if team.id is None:
            orm_team = mappers.TeamMapper.to_orm(team)
            self.session.add(orm_team)
        else:
            result = await self.session.execute(
                select(orm_models.TeamOrm)
                .where(orm_models.TeamOrm.id == team.id)
                .options(selectinload(orm_models.TeamOrm.members))
            )
            orm_model = result.scalar_one()
            mappers.TeamMapper.update_orm(orm_model, team)
