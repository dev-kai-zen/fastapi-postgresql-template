from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.user_roles import repository
from app.modules.rbac.user_roles.schema import (
    RbacUserRoleCreate,
    RbacUserRoleRead,
    RbacUserRoleUpdate,
)


def list_rbac_user_roles(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacUserRoleRead]:
    rows = repository.list_rbac_user_roles(db, skip=skip, limit=limit)
    return [RbacUserRoleRead.model_validate(row) for row in rows]


def list_rbac_user_roles_by_user_id(
    db: Session, user_id: int
) -> list[RbacUserRoleRead]:
    rows = repository.list_rbac_user_roles_by_user_id(db, user_id)
    return [RbacUserRoleRead.model_validate(row) for row in rows]


def list_rbac_user_roles_by_role_id(
    db: Session, role_id: int
) -> list[RbacUserRoleRead]:
    rows = repository.list_rbac_user_roles_by_role_id(db, role_id)
    return [RbacUserRoleRead.model_validate(row) for row in rows]


def get_rbac_user_role_by_id(db: Session, user_role_id: int) -> RbacUserRoleRead:
    row = repository.get_rbac_user_role_by_id(db, user_role_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="RBAC user-role assignment not found"
        )
    return RbacUserRoleRead.model_validate(row)


def get_rbac_user_roles_by_ids(
    db: Session, ids: list[int]
) -> list[RbacUserRoleRead]:
    rows = repository.get_rbac_user_roles_by_ids(db, ids)
    return [RbacUserRoleRead.model_validate(row) for row in rows]


def create_rbac_user_role(
    db: Session, create_data: RbacUserRoleCreate, *, assigned_by: int
) -> RbacUserRoleRead:
    try:
        row = repository.create_rbac_user_role(
            db, create_data, assigned_by=assigned_by
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "User-role assignment conflicts (duplicate user/role or invalid "
                "user/role reference)"
            ),
        ) from None
    return RbacUserRoleRead.model_validate(row)


def update_rbac_user_role(
    db: Session,
    user_role_id: int,
    update_data: RbacUserRoleUpdate,
) -> RbacUserRoleRead:
    row = repository.get_rbac_user_role_by_id(db, user_role_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="RBAC user-role assignment not found"
        )
    try:
        row = repository.update_rbac_user_role(db, row, update_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "User-role assignment conflicts (duplicate user/role or invalid "
                "user/role reference)"
            ),
        ) from None
    return RbacUserRoleRead.model_validate(row)


def delete_rbac_user_role(db: Session, user_role_id: int) -> None:
    row = repository.get_rbac_user_role_by_id(db, user_role_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="RBAC user-role assignment not found"
        )
    repository.delete_rbac_user_role(db, row)
