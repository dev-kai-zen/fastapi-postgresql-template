from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.role_permissions import repository
from app.modules.rbac.role_permissions.schema import (
    RbacRolePermissionCreate,
    RbacRolePermissionRead,
    RbacRolePermissionUpdate,
)


def list_rbac_role_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacRolePermissionRead]:
    rows = repository.list_rbac_role_permissions(db, skip=skip, limit=limit)
    return [RbacRolePermissionRead.model_validate(row) for row in rows]


def get_rbac_role_permission_by_id(
    db: Session, role_permission_id: int
) -> RbacRolePermissionRead:
    row = repository.get_rbac_role_permission_by_id(db, role_permission_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="Rbac role-permission link not found"
        )
    return RbacRolePermissionRead.model_validate(row)


def get_rbac_role_permissions_by_ids(
    db: Session, ids: list[int]
) -> list[RbacRolePermissionRead]:
    rows = repository.get_rbac_role_permissions_by_ids(db, ids)
    return [RbacRolePermissionRead.model_validate(row) for row in rows]


def create_rbac_role_permission(
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


def update_rbac_role_permission(
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


def delete_rbac_role_permission(db: Session, role_permission_id: int) -> None:
    row = repository.get_rbac_role_permission_by_id(db, role_permission_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="Rbac role-permission link not found"
        )
    repository.delete_rbac_role_permission(db, row)
