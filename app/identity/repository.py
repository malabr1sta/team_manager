from sqlalchemy import select

from app.core.repositories.base import AbstractRepository
from app.identity.orm_models import UserORM
from app.identity import models, mappers


# ── For domain logic (UoW)

class SQLAlchemyIdentityUserRepository(AbstractRepository[models.User]):
    """Domain repository for User aggregate."""

    async def get_by_id(self, user_id: int) -> models.User | None:
        result = await self.session.execute(
            select(UserORM).where(
                UserORM.id == user_id # type: ignore[arg-type]
            )
        )
        orm = result.scalar_one_or_none()
        return mappers.UserMapper.to_domain(orm) if orm else None

    async def get_by_email(self, email: str) -> models.User | None:
        result = await self.session.execute(
            select(UserORM).where(
                UserORM.email == email # type: ignore[arg-type]
            )
        )
        orm = result.scalar_one_or_none()
        return mappers.UserMapper.to_domain(orm) if orm else None

    async def save(self, domain: models.User) -> None:
        result = await self.session.execute(
            select(UserORM).where(
                UserORM.id == domain.id # type: ignore[arg-type]
            )
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            # should not happen - creates fastapi-users
            raise RuntimeError(f"UserORM with id={domain.id} not found")

        mappers.UserMapper.update_orm(orm, domain)
        self.uow._seen.add(domain)



