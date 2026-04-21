from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.permissions.model import RbacPermission
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role_permissions import repository
from app.modules.rbac.role_permissions.model import RbacRolePermissions
from app.modules.rbac.role_permissions.schema import (
    RbacPermissionBrief,
    RbacRoleBrief,
    RbacRolePermissionReadJoined,
    RbacRolePermissionUpdate,
)


def _to_joined_read(
    row: tuple[RbacRolePermissions, RbacRole, RbacPermission],
) -> RbacRolePermissionReadJoined:
    rp, role, perm = row
    return RbacRolePermissionReadJoined(
        id=rp.id,
        role_id=rp.role_id,
        permission_id=rp.permission_id,
        role=RbacRoleBrief.model_validate(role),
        permission=RbacPermissionBrief.model_validate(perm),
        created_at=rp.created_at,
        updated_at=rp.updated_at,
    )


def list_rbac_role_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.list_rbac_role_permissions(db, skip=skip, limit=limit)
    return [_to_joined_read(r) for r in rows]


def list_rbac_role_permissions_by_role_ids(
    db: Session, role_ids: list[int]
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.list_rbac_role_permissions_by_role_ids(db, role_ids)
    return [_to_joined_read(r) for r in rows]


def get_rbac_role_permissions_by_role_id(
    db: Session, role_id: int
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.get_rbac_role_permissions_by_role_id(db, role_id)
    return [_to_joined_read(r) for r in rows]


def set_rbac_role_permissions_by_role_id(
    db: Session,
    role_id: int,
    update_data: RbacRolePermissionUpdate,
) -> list[RbacRolePermissionReadJoined]:
    """Delete existing links for `role_id`, then insert `permission_ids` (DB enforces valid role/permission FKs)."""
    permission_ids = list(dict.fromkeys(update_data.permission_ids))
    try:
        rows = repository.set_rbac_role_permissions_by_role_id(
            db, role_id, permission_ids
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Role permissions conflict (duplicate or invalid permission id)",
        ) from None
    return [_to_joined_read(r) for r in rows]

