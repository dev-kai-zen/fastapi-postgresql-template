from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.rbac.user_roles import service as user_roles_service

SUPER_ADMIN_ROLE_NAME = "super_admin"


def permission_guard(
    user_id: int, db: Session, permissions: list[str], mode: str = "any"
) -> None:
    """Guard against missing or insufficient RBAC permissions."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing user ID",
        )
    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing permission",
        )

    user = user_roles_service.get_rbac_user_roles_permissions_by_user_id(
        db, user_id)

    if any(r.name == SUPER_ADMIN_ROLE_NAME for r in user.roles):
        return

    role_permissions = user.role_permissions
    if not role_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no permissions",
        )

    user_codes = {rp.permission.code for rp in role_permissions}
    required = set(permissions)

    if mode == "any":
        if user_codes & required:
            return
    else:
        if required <= user_codes:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have the required permission",
    )


def role_guard(user_id: int, db: Session, roles: list[str], mode: str = "any") -> None:
    """Guard against missing or insufficient RBAC roles."""
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing user ID",
        )
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing role",
        )

    user = user_roles_service.get_rbac_user_roles_permissions_by_user_id(
        db, user_id)
    if any(r.name == SUPER_ADMIN_ROLE_NAME for r in user.roles):
        return
    user_roles = {r.name for r in user.roles}
    required = set(roles)
    if mode == "any":
        if user_roles & required:
            return
    else:
        if required <= user_roles:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User does not have the required role",
    )
