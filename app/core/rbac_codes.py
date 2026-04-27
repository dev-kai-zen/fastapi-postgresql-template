"""Permission codes stored in `rbac_permissions.code` and used with `require_permission(...)`.

Seed or migrate these values so operator roles can grant access; `super_admin` still bypasses checks.
"""

USER_READ = "user.read"
USER_CREATE = "user.create"
USER_UPDATE = "user.update"
USER_DELETE = "user.delete"

RBAC_READ = "rbac.read"
RBAC_MANAGE = "rbac.manage"
