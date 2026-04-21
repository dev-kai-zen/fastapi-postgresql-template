from datetime import datetime
from enum import StrEnum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.modules.rbac.role.schema import RbacRoleRead
from app.modules.rbac.role_permissions.schema import RbacRolePermissionReadJoined


class UserListSortBy(StrEnum):
    """Allowed `sort_by` values for list users (must match repository mapping)."""

    ID = "id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
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
    name: str = Field(default="", max_length=255)
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

    @model_validator(mode="after")
    def fill_names_from_display_name(self) -> "UserGoogleInfo":
        if self.first_name == "" and self.last_name == "" and self.name.strip():
            parts = self.name.strip().split(None, 1)
            return self.model_copy(
                update={
                    "first_name": parts[0],
                    "last_name": parts[1] if len(parts) > 1 else "",
                }
            )
        return self


class UserCreate(BaseModel):
    google_id: str = Field(max_length=255)
    email: str = Field(max_length=320)
    phone_number: str | None = Field(default=None, max_length=255)
    first_name: str = Field(max_length=255)
    middle_name: str | None = Field(default=None, max_length=255)
    last_name: str = Field(max_length=255)
    username: str | None = Field(default=None, max_length=255)
    picture: str | None = Field(default=None, max_length=2048)
    is_active: int = Field(default=0, ge=0)
    password: str | None = Field(
        default=None,
        min_length=1,
        description="Plaintext; stored hashed. Omit for OAuth-only users.",
    )


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    google_id: str
    email: str
    phone_number: str | None
    first_name: str
    middle_name: str | None
    last_name: str
    username: str | None
    picture: str | None
    is_active: int
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class UserUpdate(BaseModel):
    google_id: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    phone_number: str | None = Field(default=None, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)
    middle_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)
    picture: str | None = Field(default=None, max_length=2048)
    is_active: int | None = Field(default=None, ge=0)
    last_login_at: datetime | None = None
    password: str | None = Field(
        default=None,
        min_length=1,
        description="Plaintext; stored hashed when set.",
    )


class UserListResponse(BaseModel):
    data: list[UserRead]
    total: int


class UserRolesAndPermissionsResponse(BaseModel):
    user: UserRead
    roles: list[RbacRoleRead]
    permissions: list[RbacRolePermissionReadJoined]

class UserCreeatRequest (BaseModel):
    user: UserCreate
    roles: list[int]
    permissions: list[int]
    user_id: int
