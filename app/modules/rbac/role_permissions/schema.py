from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


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
    code: str
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
    """Replace the role’s permission set with this list (order preserved; duplicates dropped)."""

    permission_ids: list[Annotated[int, Field(ge=1)]] = Field(
        default_factory=list)
