import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.tasks import (
    models,
    orm_models,
    mappers,
    repository
)
from app.core.custom_types import ids, role


@pytest.mark.anyio
async def test_save_creates_new_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    await async_session.commit()

    result = await async_session.execute(
        select(orm_models.TaskUserOrm)
        .where(orm_models.TaskUserOrm.id == 1)
    )
    orm_user = result.scalar_one()

    assert orm_user.id == 1
    assert orm_user.username == "leonya"


@pytest.mark.anyio
async def test_get_user(async_session):
    repo = repository.SQLAlchemyTaskUserRepository(async_session)

    user = models.TaskUser(
        id=ids.UserId(1),
        username="leonya",
    )

    await repo.save(user)
    user_1 = await repo.get_by_id(1)

    assert user_1
    assert user_1.id == 1
    assert user_1.username == "leonya"

