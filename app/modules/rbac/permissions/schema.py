from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RbacPermissionBase(BaseModel):
    code: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    group_id: int | None = None


class RbacPermissionCreate(RbacPermissionBase):
    pass


class RbacPermissionRead(RbacPermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RbacPermissionUpdate(BaseModel):
    code: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    group_id: int | None = None
