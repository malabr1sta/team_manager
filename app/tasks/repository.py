from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tasks import (
    models,
    orm_models,
    mappers
)


class SQLAlchemyTaskUserRepository:
    """Implementing a user's repository"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> models.TaskUser | None:
        result = await self.session.execute(
            select(orm_models.TaskUserOrm)
            .where(orm_models.TaskUserOrm.id == id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return mappers.TaskUserMapper.to_domain(user)

    async def save(self, user: models.TaskUser):
        result = await self.session.execute(
            select(orm_models.TaskUserOrm)
            .where(orm_models.TaskUserOrm.id == user.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            self.session.add(mappers.TaskUserMapper.to_orm(user))
            return
        mappers.TaskUserMapper.update_orm(orm, user)

