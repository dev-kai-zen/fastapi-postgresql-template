from datetime import datetime
from pydantic import BaseModel, Field


class RbacGroupBase(BaseModel):
    name: str = Field(max_length=255)


class RbacGroupCreate(RbacGroupBase):
    pass

class RbacGroupRead(RbacGroupBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

class RbacGroupUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    updated_at: datetime | None = None
    deleted_at: datetime | None = None