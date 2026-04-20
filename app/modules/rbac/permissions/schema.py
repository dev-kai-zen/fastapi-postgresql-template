from datetime import datetime

from pydantic import BaseModel, Field


class RbacPermissionBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    group_id: int | None = None


class RbacPermissionCreate(RbacPermissionBase):
    pass


class RbacPermissionRead(RbacPermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime


class RbacPermissionUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    group_id: int | None = None
