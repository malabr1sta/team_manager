from fastapi_users import schemas
from pydantic import ConfigDict


class UserRead(schemas.BaseUser[int]):
    username: str
    deleted: bool
    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None
