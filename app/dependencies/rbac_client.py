"""HTTP-layer adapter: maps RBAC checks to `rbac_guards` only.

Guards intentionally live next to RBAC (they load roles/permissions via `user_roles` service and
raise `HTTPException`). Keep route-level rules here and in `rbac_deps` so services stay free of
authorization policy duplication.
"""

from sqlalchemy.orm import Session

from app.modules.rbac import rbac_guards


class RbacClient:
    def assert_permissions(
        self,
        user_id: int,
        db: Session,
        permissions: list[str],
        *,
        mode: str = "any",
    ) -> None:
        rbac_guards.permission_guard(user_id, db, permissions, mode=mode)

    def assert_roles(
        self,
        user_id: int,
        db: Session,
        roles: list[str],
        *,
        mode: str = "any",
    ) -> None:
        rbac_guards.role_guard(user_id, db, roles, mode=mode)
