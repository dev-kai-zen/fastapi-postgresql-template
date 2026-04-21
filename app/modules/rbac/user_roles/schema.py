from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RbacUserRoleCreate(BaseModel):
    """Assign a role to a user. `assigned_by` is set from the access token in the API."""

    user_id: int = Field(ge=1)
    role_id: int = Field(ge=1)


class RbacUserRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    assigned_by: int
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime


class RbacUserRoleUpdate(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    role_id: int | None = Field(default=None, ge=1)
