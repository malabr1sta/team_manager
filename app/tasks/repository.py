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


class SQLAlchemyTaskMemberRepository:
    """Implementing a member's repository"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user(
        self, user_id: int
    ) -> list[models.MemberTask]:

        result = await self.session.execute(
            select(orm_models.TaskMemberOrm)
            .where(orm_models.TaskMemberOrm.user_id == user_id)
        )
        orms = result.scalars().all()
        return [mappers.TaskMemberMapper.to_domain(orm) for orm in orms]


    async def get_by_user_and_team(
        self,
        user_id: int,
        team_id: int
    ) -> list[models.MemberTask]:

        result = await self.session.execute(
            select(orm_models.TaskMemberOrm)
            .where(
                orm_models.TaskMemberOrm.user_id == user_id,
                orm_models.TaskMemberOrm.team_id == team_id
            )
        )
        orms = result.scalars().all()
        return [mappers.TaskMemberMapper.to_domain(orm) for orm in orms]


    async def save(self, member: models.MemberTask) -> None:
        result = await self.session.execute(
            select(orm_models.TaskMemberOrm)
            .where(
                orm_models.TaskMemberOrm.user_id == member.user_id,
                orm_models.TaskMemberOrm.team_id == member.team_id,
                orm_models.TaskMemberOrm.role == member.role
            )
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            self.session.add(mappers.TaskMemberMapper.to_orm(member))
            return
        mappers.TaskMemberMapper.update_orm(orm, member)






