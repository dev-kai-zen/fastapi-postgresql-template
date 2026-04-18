from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


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
    deleted_at: datetime | None


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
    deleted_at: datetime | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
