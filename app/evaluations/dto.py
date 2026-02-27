from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.custom_types import grade as grade_type


class CreateEvaluationCommand(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: int | None = Field(default=None, gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    grade: grade_type.Grade = Field(...)


class EvaluationReadDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int
    team_id: int
    task_id: int
    grade: grade_type.Grade
    created_at: datetime


class EvaluationListDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[EvaluationReadDTO]
    total: int


class EvaluationAverageDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    average: float | None
