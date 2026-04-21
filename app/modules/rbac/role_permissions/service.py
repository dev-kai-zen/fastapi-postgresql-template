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
    RbacRolePermissionCreate,
    RbacRolePermissionRead,
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


def get_rbac_role_permission_by_id(
    db: Session, role_permission_id: int
) -> RbacRolePermissionReadJoined:
    row = repository.get_rbac_role_permission_by_id_with_join(db, role_permission_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="Rbac role-permission link not found"
        )
    return _to_joined_read(row)


def list_rbac_role_permissions_by_ids(
    db: Session, ids: list[int]
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.list_rbac_role_permissions_by_ids_with_join(db, ids)
    return [_to_joined_read(r) for r in rows]


def list_rbac_role_permissions_by_role_ids(
    db: Session, role_ids: list[int]
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.list_rbac_role_permissions_by_role_ids_with_join(db, role_ids)
    return [_to_joined_read(r) for r in rows]


def list_rbac_role_permissions_by_role_id(
    db: Session, role_id: int
) -> list[RbacRolePermissionReadJoined]:
    rows = repository.list_rbac_role_permissions_by_role_id_with_join(db, role_id)
    return [_to_joined_read(r) for r in rows]


def create_rbac_role_permissions(
    db: Session, create_data: RbacRolePermissionCreate
) -> RbacRolePermissionRead:
    try:
        row = repository.create_rbac_role_permission(db, create_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Role-permission link conflicts (duplicate or invalid role/permission)",
        ) from None
    return RbacRolePermissionRead.model_validate(row)


def update_rbac_role_permissions(
    db: Session,
    role_permission_id: int,
    update_data: RbacRolePermissionUpdate,
) -> RbacRolePermissionRead:
    row = repository.get_rbac_role_permission_by_id(db, role_permission_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="Rbac role-permission link not found"
        )
    try:
        row = repository.update_rbac_role_permission(db, row, update_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Role-permission link conflicts (duplicate or invalid role/permission)",
        ) from None
    return RbacRolePermissionRead.model_validate(row)


def delete_rbac_role_permissions(db: Session, role_permission_id: int) -> None:
    row = repository.get_rbac_role_permission_by_id(db, role_permission_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="Rbac role-permission link not found"
        )
    repository.delete_rbac_role_permission(db, row)
