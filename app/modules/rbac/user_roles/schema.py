from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.modules.rbac.role.schema import RbacRoleRead
from app.modules.rbac.role_permissions.schema import RbacRolePermissionReadJoined


class RbacUserRoleUserBrief(BaseModel):
    """Subset of user fields for RBAC joins (owned by `users`; mapped in `users_client`)."""

    id: int
    email: str
    first_name: str
    last_name: str
    picture: str | None = None


class RbacUserRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    assigned_by: int
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime


class RbacUserRolesListItemWithUser(BaseModel):
    """User info with distinct roles (from the current list page, grouped by user)."""

    user: RbacUserRoleUserBrief
    roles: list[RbacRoleRead]


class RbacUserRolesForUserId(BaseModel):
    """One user id and that user’s roles (order matches `user_ids` on batch endpoints)."""

    user_id: int
    roles: list[RbacRoleRead]


class RbacUserRolesDetailByUserId(BaseModel):
    """User’s roles plus union of role→permission links, deduped by `permission_id`."""

    user_id: int
    roles: list[RbacRoleRead]
    role_permissions: list[RbacRolePermissionReadJoined]


class RbacUserRoleUpdateByUserId(BaseModel):
    """Replace all role assignments for the user with this role id set."""

    role_ids: list[Annotated[int, Field(ge=1)]] = Field(default_factory=list)
