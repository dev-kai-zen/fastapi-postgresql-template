from datetime import datetime

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


class RbacUserRoleCreate(BaseModel):
    """Assign a role to a user. `assigned_by` is set from the access token in the API."""

    user_id: int = Field(ge=1)
    role_id: int = Field(ge=1)


class RbacUserRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    role_id: int
    assigned_by: int
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime


class RbacUserRoleUpdate(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    role_id: int | None = Field(default=None, ge=1)


class RbacUserRoleReadJoined(BaseModel):
    """Assignment with subject user, role, and assigner (same-module role join + users via client)."""

    id: int
    user_id: int
    role_id: int
    assigned_by: int
    assigned_at: datetime
    created_at: datetime
    updated_at: datetime
    user: RbacUserRoleUserBrief
    role: RbacRoleRead
    assigned_by_user: RbacUserRoleUserBrief


class RbacUserRoleReadJoinedWithPermissions(RbacUserRoleReadJoined):
    """Per-assignment row plus permissions linked to `role_id`."""

    permissions: list[RbacRolePermissionReadJoined]
