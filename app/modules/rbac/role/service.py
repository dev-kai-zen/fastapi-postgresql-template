from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.role import repository
from app.modules.rbac.role.schema import RbacRoleCreate, RbacRoleRead, RbacRoleUpdate


def list_rbac_roles(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacRoleRead]:
    rows = repository.list_rbac_roles(db, skip=skip, limit=limit)
    return [RbacRoleRead.model_validate(row) for row in rows]


def get_rbac_role_by_id(db: Session, role_id: int) -> RbacRoleRead:
    rbac_role = repository.get_rbac_role_by_id(db, role_id)
    if rbac_role is None:
        raise HTTPException(status_code=404, detail="Rbac role not found")
    return RbacRoleRead.model_validate(rbac_role)


def list_rbac_roles_by_ids(db: Session, ids: list[int]) -> list[RbacRoleRead]:
    rows = repository.list_rbac_roles_by_ids(db, ids)
    return [RbacRoleRead.model_validate(row) for row in rows]


def create_rbac_role(db: Session, create_data: RbacRoleCreate) -> RbacRoleRead:
    try:
        rbac_role = repository.create_rbac_role(db, create_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac role name already exists",
        ) from None
    return RbacRoleRead.model_validate(rbac_role)


def update_rbac_role(
    db: Session, role_id: int, update_data: RbacRoleUpdate
) -> RbacRoleRead:
    rbac_role = repository.get_rbac_role_by_id(db, role_id)
    if rbac_role is None:
        raise HTTPException(status_code=404, detail="Rbac role not found")
    try:
        rbac_role = repository.update_rbac_role(db, rbac_role, update_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac role name already exists",
        ) from None
    return RbacRoleRead.model_validate(rbac_role)


def delete_rbac_role(db: Session, role_id: int) -> None:
    rbac_role = repository.get_rbac_role_by_id(db, role_id)
    if rbac_role is None:
        raise HTTPException(status_code=404, detail="Rbac role not found")
    repository.delete_rbac_role(db, rbac_role)
