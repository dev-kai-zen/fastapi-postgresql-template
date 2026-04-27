"""RBAC entrypoint for the HTTP dependency layer. Wraps `rbac_guards` for route protection."""

from sqlalchemy.orm import Session

from app.modules.rbac import rbac_guards


class RbacClient:
    async def assert_permissions(
        self,
        user_id: int,
        db: Session,
        permissions: list[str],
        *,
        mode: str = "any",
    ) -> None:
        await rbac_guards.permission_guard(
            user_id, db, permissions, mode=mode
        )

    def assert_roles(
        self,
        user_id: int,
        db: Session,
        roles: list[str],
        *,
        mode: str = "any",
    ) -> None:
        rbac_guards.role_guard(user_id, db, roles, mode=mode)

