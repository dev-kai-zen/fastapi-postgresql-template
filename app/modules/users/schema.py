from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class UserListSortBy(StrEnum):
    """Allowed `sort_by` values for list users (must match repository mapping)."""
    ID = "id"
    NAME = "name"
    EMAIL = "email"
    CREATED_AT = "created_at"
    IS_ACTIVE = "is_active"


class UserListSortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class UserGoogleInfo(BaseModel):
    """Payload from Google userinfo, normalized for the users module (client boundary)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    google_id: str = Field(
        max_length=255,
        validation_alias=AliasChoices("id", "google_id"),
        serialization_alias="google_id",
    )
    email: str = Field(max_length=320)
    name: str = Field(max_length=255)
    first_name: str = Field(
        default="",
        max_length=255,
        validation_alias=AliasChoices("given_name", "first_name"),
    )
    last_name: str = Field(
        default="",
        max_length=255,
        validation_alias=AliasChoices("family_name", "last_name"),
    )
    picture: str | None = Field(default=None, max_length=2048)


class UserBase(BaseModel):
    google_id: str = Field(max_length=255)
    email: str = Field(max_length=320)
    name: str = Field(max_length=255)
    picture: str | None = Field(default=None, max_length=2048)
    id_number: str | None = Field(default=None, max_length=255)
    role_id: int | None = None
    flags: Any | None = None
    is_active: int = 0
    last_logged_in: datetime | None = None


class UserCreate(UserBase):
    pass


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    picture: str | None
    id_number: str | None
    role_id: int | None
    flags: Any | None
    is_active: int
    last_logged_in: datetime | None
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    google_id: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    name: str | None = Field(default=None, max_length=255)
    picture: str | None = Field(default=None, max_length=2048)
    id_number: str | None = Field(default=None, max_length=255)
    role_id: int | None = None
    flags: Any | None = None
    is_active: int | None = None
    last_logged_in: datetime | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    data: list[UserRead]
    total: int