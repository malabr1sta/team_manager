from pydantic import BaseModel, Field, ConfigDict, EmailStr


class DeleteUserCommand(BaseModel):
    model_config = ConfigDict(frozen=True)
    user_id: int | None = Field(..., gt=0, description="User ID to delete")


class UpdateUserCommand(BaseModel):
    model_config = ConfigDict(frozen=True)
    user_id: int | None = Field(..., gt=0, description="User ID to update")
    username: str | None = Field(
        None, min_length=1, max_length=100, description="New username"
    )


class UpdateUserResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    user_id: int
    email: str
    username: str
