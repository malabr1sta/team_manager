from fastapi import APIRouter, Depends

from deps.user import fastapi_users, auth_backend, current_active_user
from app.identity import schemas
from app.identity.orm_models import UserORM


auth_router = APIRouter()

auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
auth_router.include_router(
    fastapi_users.get_register_router(schemas.UserRead, schemas.UserCreate),
    prefix="/auth",
    tags=["auth"],
)
# router.include_router(
#     fastapi_users.get_verify_router(schemas.UserRead),
#     prefix="/auth",
#     tags=["auth"],
# )
# router.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# router.include_router(
#     fastapi_users.get_users_router(schemas.UserRead, schemas.UserUpdate),
#     prefix="/users",
#     tags=["users"],
# )


users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@users_router.get("/me")
async def get_me(user: UserORM = Depends(current_active_user)):
    return user

