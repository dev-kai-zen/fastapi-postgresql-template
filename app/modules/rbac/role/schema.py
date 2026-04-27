from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RbacRoleBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class RbacRoleCreate(RbacRoleBase):
    pass


class RbacRoleRead(RbacRoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RbacRoleUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
