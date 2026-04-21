from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RbacRolePermissionCreate(BaseModel):
    role_id: int = Field(ge=1)
    permission_id: int = Field(ge=1)


class RbacRolePermissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    permission_id: int
    created_at: datetime
    updated_at: datetime


class RbacRoleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class RbacPermissionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class RbacRolePermissionReadJoined(BaseModel):
    """Role–permission link with nested `role` and `permission` rows (same-module join)."""

    id: int
    role_id: int
    permission_id: int
    role: RbacRoleBrief
    permission: RbacPermissionBrief
    created_at: datetime
    updated_at: datetime


class RbacRolePermissionUpdate(BaseModel):
    role_id: int | None = Field(default=None, ge=1)
    permission_id: int | None = Field(default=None, ge=1)
