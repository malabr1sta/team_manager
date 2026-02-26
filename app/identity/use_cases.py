from app.identity.unit_of_work import IdentitySQLAlchemyUnitOfWork
from app.identity.custom_exception import UserNotFoundException
from app.identity import dto
from fastapi import HTTPException
from app.identity.custom_exception import UserDeleteException


class DeleteUserUseCase:
    """Use case for soft-deleting a user by ID."""

    def __init__(self, uow: IdentitySQLAlchemyUnitOfWork):
        """Initialize with Unit of Work."""
        self.uow = uow

    async def execute(self, command: dto.DeleteUserCommand) -> None:
        """
        Mark user as deleted and persist the change.

        Raises UserNotFoundException if user does not exist.
        """
        user = await self.uow.repos.user.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundException(f"User {command.user_id} not found")
        user.delete()
        await self.uow.repos.user.save(user)
        await self.uow.commit()


class UpdateUserUseCase:
    """Use case for updating user email and/or username."""

    def __init__(self, uow: IdentitySQLAlchemyUnitOfWork):
        """Initialize with Unit of Work."""
        self.uow = uow

    async def execute(
            self, command: dto.UpdateUserCommand
    ) -> dto.UpdateUserResult:
        """
        Apply partial updates to a user and persist the change.

        Raises UserNotFoundException if user does not exist.
        Returns updated user data.
        """
        user = await self.uow.repos.user.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundException(f"User {command.user_id} not found")
        user.update(username=command.username)
        await self.uow.repos.user.save(user)
        await self.uow.commit()
        return dto.UpdateUserResult(
            user_id=command.user_id,
            email=user.email,
            username=user.username,
        )


def map_identity_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, UserNotFoundException):
        return HTTPException(404, str(exc))
    if isinstance(exc, UserDeleteException):
        return HTTPException(409, str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(400, "Invalid user payload")
    return HTTPException(500, "Internal server error")
