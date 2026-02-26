from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateTaskCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    team_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    deadline: datetime
    actor_user_id: int | None = Field(default=None, gt=0)


class AssignExecutorCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: int = Field(..., gt=0)
    executor_id: int = Field(..., gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)


class UpdateTaskCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: int | None = Field(default=None, gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, description="open|in_progress|done")
    deleted: bool | None = None


class AddCommentCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: int | None = Field(default=None, gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    text: str = Field(..., min_length=1)


class TaskReadDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    team_id: int | None
    supervisor_id: int
    executor_id: int | None
    title: str
    description: str
    status: str
    deadline: datetime
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False


class TaskListDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[TaskReadDTO]
    total: int
    limit: int
    offset: int


class CommentReadDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    task_id: int
    author_id: int
    text: str
    created_at: datetime | None = None
