"""Import models from this package so they are registered on Base.metadata."""

from .base import Base

import app.core.refresh_token.model as auth_refresh_token_model
import app.modules.users.model as users_model
import app.modules.rbac.group.model as rbac_group_model
import app.modules.rbac.role.model as rbac_role_model
import app.modules.rbac.permissions.model as rbac_permissions_model
import app.modules.rbac.role_permissions.model as rbac_role_permissions_model

__all__ = ["Base", "auth_refresh_token_model", "users_model", "rbac_group_model",
           "rbac_role_model", "rbac_permissions_model", "rbac_role_permissions_model"]
