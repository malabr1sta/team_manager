from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps.user import (
    UserDepend,
    fastapi_users,
    auth_backend,
    user_uow,
)
from app.identity import schemas, dto, use_cases
from app.identity.unit_of_work import IdentitySQLAlchemyUnitOfWork


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
async def get_me(user: UserDepend):
    return user


@users_router.patch("/me")
async def update_me(
    command_body: dto.UpdateUserCommand,
    user: UserDepend,
    uow: Annotated[IdentitySQLAlchemyUnitOfWork, Depends(user_uow)],
):
    command = command_body.model_copy(update={"user_id": user.id})
    try:
        return await use_cases.UpdateUserUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_identity_exception(exc)


@users_router.delete("/me", status_code=204)
async def delete_me(
    user: UserDepend,
    uow: Annotated[IdentitySQLAlchemyUnitOfWork, Depends(user_uow)],
):
    command = dto.DeleteUserCommand(user_id=user.id)
    try:
        await use_cases.DeleteUserUseCase(uow).execute(command)
    except Exception as exc:
        raise use_cases.map_identity_exception(exc)
