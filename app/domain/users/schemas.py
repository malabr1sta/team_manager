from fastapi_users import schemas

from app.domain.users import model as user_model


class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    role: user_model.RoleEnum

class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    role: user_model.RoleEnum

class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
    role: user_model.RoleEnum | None = None
