from sqlalchemy import select

from app.core.repositories.base import AbstractRepository
from app.core.custom_types import ids
from app.tasks import (
    models,
    orm_models,
    mappers
)


class SQLAlchemyTaskUserRepository(AbstractRepository[models.TaskUser]):
    """Implementing a user's repository"""

    async def get_by_id(self, id: int) -> models.TaskUser | None:
        result = await self.session.execute(
            select(orm_models.TaskUserOrm)
            .where(orm_models.TaskUserOrm.id == id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        return mappers.TaskUserMapper.to_domain(user)

    async def save(self, domain: models.TaskUser):
        result = await self.session.execute(
            select(orm_models.TaskUserOrm)
            .where(orm_models.TaskUserOrm.id == domain.id)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            self.session.add(mappers.TaskUserMapper.to_orm(domain))
            return
        mappers.TaskUserMapper.update_orm(orm, domain)


class SQLAlchemyTaskMemberRepository(AbstractRepository[models.MemberTask]):
    """Implementing a member's repository"""

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


    async def save(self, domain: models.MemberTask) -> None:
        result = await self.session.execute(
            select(orm_models.TaskMemberOrm)
            .where(
                orm_models.TaskMemberOrm.user_id == domain.user_id,
                orm_models.TaskMemberOrm.team_id == domain.team_id,
                orm_models.TaskMemberOrm.role == domain.role
            )
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            self.session.add(mappers.TaskMemberMapper.to_orm(domain))
            return
        mappers.TaskMemberMapper.update_orm(orm, domain)


class SQLAlchemyTeamRepository(AbstractRepository[models.Team]):
    """Implementing a team's repository"""

    async def get_by_id(self, id: int) -> models.Team | None:
        result = await self.session.execute(
            select(orm_models.TaskTeamOrm)
            .where(orm_models.TaskTeamOrm.id == id)
        )
        orm_team = result.scalar_one_or_none()
        if orm_team is None:
            return
        return mappers.TaskTeamMapper.to_domain(orm_team)

    async def save(self, domain: models.Team) -> None:
        result = await self.session.execute(
            select(orm_models.TaskTeamOrm)
            .where(orm_models.TaskTeamOrm.id == domain.id)
        )
        orm_team = result.scalar_one_or_none()
        if orm_team is None:
            self.session.add(mappers.TaskTeamMapper.to_orm(domain))
            return
        mappers.TaskTeamMapper.update_orm(orm_team, domain)



class SQLAlchemyTaskCommentRepository(AbstractRepository[models.Comment]):
    """Implementing a comment's repository"""

    async def get_by_task_id(self, task_id: int) ->  list[models.Comment]:
        result = await self.session.execute(
            select(orm_models.CommentOrm)
            .where(orm_models.CommentOrm.task_id == task_id)
        )
        orms = result.scalars().all()
        return [mappers.TaskCommentMapper.to_domain(orm) for orm in orms]

    async def save(self, domain: models.Comment) -> None:
        result = await self.session.execute(
            select(orm_models.CommentOrm)
            .where(orm_models.CommentOrm.id == domain.id)
        )

        orm_comment = result.scalar_one_or_none()
        if orm_comment is None:
            orm_comment = mappers.TaskCommentMapper.to_orm(domain)
            self.session.add(orm_comment)
            await self.session.flush()
            domain._id = ids.CommentId(orm_comment.id)
            return
        mappers.TaskCommentMapper.update_orm(orm_comment, domain)


class SQLAlchemyTaskRepository(AbstractRepository[models.Task]):
    """Implementing a task's repository"""

    async def get_by_id(self, id: int) -> models.Task | None:
        result = await self.session.execute(
            select(orm_models.TaskOrm)
            .where(orm_models.TaskOrm.id == id)
        )
        task_orm = result.scalar_one_or_none()
        if task_orm is None:
            return None
        return mappers.TaskMapper.to_domain(task_orm)


    async def get_by_supervisor(self, id: int) -> list[models.Task]:
        result = await self.session.execute(
            select(orm_models.TaskOrm)
            .where(orm_models.TaskOrm.supervisor_id == id)
        )
        tasks_orm = result.scalars().all()
        return [mappers.TaskMapper.to_domain(task) for task in tasks_orm]

    async def get_by_team(self, id: int) -> list[models.Task]:
        result = await self.session.execute(
            select(orm_models.TaskOrm)
            .where(orm_models.TaskOrm.team_id == id)
        )
        tasks_orm = result.scalars().all()
        return [mappers.TaskMapper.to_domain(task) for task in tasks_orm]


    async def get_by_executor(self, id: int) -> list[models.Task]:
        result = await self.session.execute(
            select(orm_models.TaskOrm)
            .where(orm_models.TaskOrm.executor_id == id)
        )
        tasks_orm = result.scalars().all()
        return [mappers.TaskMapper.to_domain(task) for task in tasks_orm]

    async def save(self, domain: models.Task) -> None:
        result = await self.session.execute(
            select(orm_models.TaskOrm)
            .where(orm_models.TaskOrm.id == domain.id)
        )
        task_orm = result.scalar_one_or_none()
        if task_orm is None:
            orm_task = mappers.TaskMapper.to_orm(domain)
            self.session.add(orm_task)
            await self.session.flush()
            domain._id = ids.TaskId(orm_task.id)
            return
        mappers.TaskMapper.update_orm(task_orm, domain)
