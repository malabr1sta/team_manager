import json
from fastapi_users.db import SQLAlchemyUserDatabase
from pydantic import BaseModel, ConfigDict

from app.domain.users import model as user_model
from app.domain.users import schemas as user_schemas


CACHE_TTL = 300



class CachedUserDatabase(SQLAlchemyUserDatabase):
    def __init__(self, session, user_table, redis, oauth_account_table=None):
        super().__init__(session, user_table, oauth_account_table)
        self.redis = redis

    async def _get_from_cache(self, key: str) -> user_schemas.UserRead | None:
        cached = await self.redis.get(key)
        if not cached:
            return None
        return user_schemas.UserRead.model_validate(json.loads(cached))

    async def _set_cache(self, user: user_model.User):
        data = user_schemas.UserRead.model_validate(user).model_dump()
        await self.redis.set(
            f"user:{user.id}",
            json.dumps(data),
            ex=CACHE_TTL,
        )
        await self.redis.set(
            f"user:email:{user.email.lower()}",
            json.dumps(data),
            ex=CACHE_TTL,
        )

    async def _delete_cache(self, user: user_model.User):
        await self.redis.delete(f"user:{user.id}")
        await self.redis.delete(f"user:email:{user.email.lower()}")

    async def get(self, id: str) -> user_schemas.UserRead | None:
        key = f"user:{id}"
        cached = await self._get_from_cache(key)
        if cached:
            return cached

        user = await super().get(id)
        if not user:
            return None

        await self._set_cache(user)
        return user_schemas.UserRead.model_validate(user)

    async def get_by_email(self, email: str) -> user_schemas.UserRead | None:
        key = f"user:email:{email.lower()}"
        cached = await self._get_from_cache(key)
        if cached:
            return cached

        user = await super().get_by_email(email)
        if not user:
            return None

        await self._set_cache(user)
        return user_schemas.UserRead.model_validate(user)

    async def create(self, create_dict: dict) -> user_schemas.UserRead:
        user = await super().create(create_dict)
        await self._set_cache(user)
        return user_schemas.UserRead.model_validate(user)

    async def update(self, user: user_model.User, update_dict: dict) -> user_schemas.UserRead:
        user = await super().update(user, update_dict)
        await self._set_cache(user)
        return user_schemas.UserRead.model_validate(user)

    async def delete(self, user: user_model.User) -> None:
        await super().delete(user)
        await self._delete_cache(user)
