from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CreateTeamCommand(BaseModel):
    """Command to create a new team."""

    model_config = ConfigDict(frozen=True)

    team_name: str = Field(
        ..., min_length=1, max_length=255, description="Team name"
    )
    user_id: int | None = Field(
        default=None, gt=0, description="Creator user ID"
    )


class CreateTeamResult(BaseModel):
    """Result of team creation."""

    model_config = ConfigDict(frozen=True)

    team_id: int = Field(..., description="Created team ID")
    team_name: str = Field(..., description="Team name")
    admin_user_id: int | None = Field(..., description="Admin ID")


class AddMemberCommand(BaseModel):
    """Command to add a member to a team."""

    model_config = ConfigDict(frozen=True)
    team_id: int | None = Field(default=None, gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    target_user_id: int = Field(..., gt=0)
    role: str = Field(..., description="member|manager|admin")


class RemoveMemberCommand(BaseModel):
    model_config = ConfigDict(frozen=True)
    team_id: int = Field(..., gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    target_user_id: int = Field(..., gt=0)
    role: str = Field(..., description="member|manager|admin")


class ChangeMemberRoleCommand(BaseModel):
    model_config = ConfigDict(frozen=True)
    team_id: int | None = Field(default=None, gt=0)
    actor_user_id: int | None = Field(default=None, gt=0)
    target_user_id: int | None = Field(default=None, gt=0)
    old_role: str = Field(..., description="member|manager|admin")
    new_role: str = Field(..., description="member|manager|admin")


class MemberReadDTO(BaseModel):
    """DTO for reading team member data."""
    model_config = ConfigDict(frozen=True, from_attributes=True)

    user_id: int
    role: str
    joined_at: datetime | None = None


class TeamReadResponsDTO(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    user_id: int | None
    team_id: int


class TeamReadDTO(BaseModel):
    """DTO for reading team data."""
    model_config = ConfigDict(frozen=True, from_attributes=True)

    id: int
    name: str
    members: list[MemberReadDTO] = Field(default_factory=list)
    members_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None

    is_admin: bool = False
    is_member: bool = True


class TeamListDTO(BaseModel):
    model_config = ConfigDict(frozen=True)
    items: list[TeamReadDTO]
    total: int
