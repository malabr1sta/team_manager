from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.teams import (
    models,
    orm_models,
    mappers
)


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
