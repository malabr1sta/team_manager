from datetime import datetime

from sqlalchemy import and_, select

from app.core.repositories.base import AbstractRepository
from app.evaluations import mappers, models, orm_models


class SQLAlchemyEvaluationUserRepository(AbstractRepository[models.User]):
    async def get_by_id(self, id: int) -> models.User | None:
        result = await self.session.execute(
            select(orm_models.EvaluationUserOrm).where(
                orm_models.EvaluationUserOrm.id == id
            )
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            return None
        user = mappers.EvaluationUserMapper.to_domain(user_orm)
        eval_result = await self.session.execute(
            select(orm_models.EvaluationOrm).where(
                orm_models.EvaluationOrm.user_id == id
            )
        )
        eval_orms = eval_result.scalars().all()
        user._evaluations = [
            mappers.EvaluationMapper.to_domain(eval_orm)
            for eval_orm in eval_orms
        ]
        return user

    async def save(self, domain: models.User):
        result = await self.session.execute(
            select(orm_models.EvaluationUserOrm).where(
                orm_models.EvaluationUserOrm.id == domain.id
            )
        )
        user_orm = result.scalar_one_or_none()
        if user_orm is None:
            self.session.add(mappers.EvaluationUserMapper.to_orm(domain))
            return
        mappers.EvaluationUserMapper.update_orm(user_orm, domain)


class SQLAlchemyEvaluationTaskRepository(AbstractRepository[models.Task]):
    async def get_by_id(self, id: int) -> models.Task | None:
        result = await self.session.execute(
            select(orm_models.EvaluationTaskOrm).where(
                orm_models.EvaluationTaskOrm.id == id
            )
        )
        task_orm = result.scalar_one_or_none()
        if task_orm is None:
            return None
        return mappers.EvaluationTaskMapper.to_domain(task_orm)

    async def save(self, domain: models.Task):
        result = await self.session.execute(
            select(orm_models.EvaluationTaskOrm).where(
                orm_models.EvaluationTaskOrm.id == domain.id
            )
        )
        task_orm = result.scalar_one_or_none()
        if task_orm is None:
            self.session.add(mappers.EvaluationTaskMapper.to_orm(domain))
            return
        mappers.EvaluationTaskMapper.update_orm(task_orm, domain)


class SQLAlchemyEvaluationRepository(AbstractRepository[models.Evaluation]):
    async def save(self, domain: models.Evaluation):
        self.session.add(mappers.EvaluationMapper.to_orm(domain))

    async def get_by_user(
        self,
        user_id: int,
        team_id: int | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[models.Evaluation]:
        conditions = [orm_models.EvaluationOrm.user_id == user_id]
        if team_id is not None:
            conditions.append(orm_models.EvaluationOrm.team_id == team_id)
        if start is not None:
            conditions.append(orm_models.EvaluationOrm.created_dttm >= start)
        if end is not None:
            conditions.append(orm_models.EvaluationOrm.created_dttm <= end)
        result = await self.session.execute(
            select(orm_models.EvaluationOrm).where(and_(*conditions))
        )
        eval_orms = result.scalars().all()
        return [mappers.EvaluationMapper.to_domain(eval_orm) for eval_orm in eval_orms]
