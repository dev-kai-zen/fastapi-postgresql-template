from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.modules.rbac.permissions import repository
from app.modules.rbac.permissions.schema import (
    RbacPermissionCreate,
    RbacPermissionRead,
    RbacPermissionUpdate,
)


def list_rbac_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacPermissionRead]:
    rows = repository.list_rbac_permissions(db, skip=skip, limit=limit)
    return [RbacPermissionRead.model_validate(row) for row in rows]


def get_rbac_permission_by_id(db: Session, permission_id: int) -> RbacPermissionRead:
    rbac_permission = repository.get_rbac_permission_by_id(db, permission_id)
    if rbac_permission is None:
        raise HTTPException(status_code=404, detail="Rbac permission not found")
    return RbacPermissionRead.model_validate(rbac_permission)


def get_rbac_permissions_by_ids(
    db: Session, ids: list[int]
) -> list[RbacPermissionRead]:
    rows = repository.get_rbac_permissions_by_ids(db, ids)
    return [RbacPermissionRead.model_validate(row) for row in rows]


def create_rbac_permission(
    db: Session, create_data: RbacPermissionCreate
) -> RbacPermissionRead:
    try:
        rbac_permission = repository.create_rbac_permission(db, create_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac permission code already exists",
        ) from None
    return RbacPermissionRead.model_validate(rbac_permission)


def update_rbac_permission(
    db: Session, permission_id: int, update_data: RbacPermissionUpdate
) -> RbacPermissionRead:
    rbac_permission = repository.get_rbac_permission_by_id(db, permission_id)
    if rbac_permission is None:
        raise HTTPException(status_code=404, detail="Rbac permission not found")
    try:
        rbac_permission = repository.update_rbac_permission(
            db, rbac_permission, update_data
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac permission code already exists",
        ) from None
    return RbacPermissionRead.model_validate(rbac_permission)


def delete_rbac_permission(db: Session, permission_id: int) -> None:
    rbac_permission = repository.get_rbac_permission_by_id(db, permission_id)
    if rbac_permission is None:
        raise HTTPException(status_code=404, detail="Rbac permission not found")
    repository.delete_rbac_permission(db, rbac_permission)
