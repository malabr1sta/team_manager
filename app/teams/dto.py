from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

from app.core.custom_types import ids, role
from app.teams import models, custom_exception


class CreateTeamCommand(BaseModel):
    """Command to create a new team."""

    model_config = ConfigDict(frozen=True)

    user_id: int = Field(..., gt=0, description="Creator user ID")
    team_name: str = Field(
        ..., min_length=1, max_length=255, description="Team name"
    )


class CreateTeamResult(BaseModel):
    """Result of team creation."""

    model_config = ConfigDict(frozen=True)

    team_id: int = Field(..., description="Created team ID")
    team_name: str = Field(..., description="Team name")
    admin_user_id: int = Field(..., description="Admin ID")


class AddMemberCommand(BaseModel):
    """Command to add a member to a team."""

    model_config = ConfigDict(frozen=True)
