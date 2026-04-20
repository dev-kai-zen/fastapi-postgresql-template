from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.modules.rbac.group.schema import RbacGroupRead, RbacGroupCreate, RbacGroupUpdate
from app.modules.rbac.group import repository

from fastapi import HTTPException


def list_rbac_groups(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacGroupRead]:
    rbac_groups = repository.list_rbac_groups(db, skip=skip, limit=limit)
    return [RbacGroupRead.model_validate(rbac_group) for rbac_group in rbac_groups]

def get_rbac_group_by_id(db: Session, group_id: int) -> RbacGroupRead:
    rbac_group = repository.get_rbac_group_by_id(db, group_id)
    if rbac_group is None:
        raise HTTPException(status_code=404, detail="Rbac group not found")
    return RbacGroupRead.model_validate(rbac_group)

def get_rbac_group_by_ids(db: Session, ids: list[int]) -> list[RbacGroupRead]:
    rbac_groups = repository.get_rbac_group_by_ids(db, ids)
    return [RbacGroupRead.model_validate(rbac_group) for rbac_group in rbac_groups]


def create_rbac_group(db: Session, create_data: RbacGroupCreate) -> RbacGroupRead:
    try:
        rbac_group = repository.create_rbac_group(db, create_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac group name already exists",
        ) from None
    return RbacGroupRead.model_validate(rbac_group)


def update_rbac_group(db: Session, group_id: int, update_data: RbacGroupUpdate) -> RbacGroupRead:
    rbac_group = repository.get_rbac_group_by_id(db, group_id)
    if rbac_group is None:
        raise HTTPException(status_code=404, detail="Rbac group not found")
    try:
        rbac_group = repository.update_rbac_group(db, rbac_group, update_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Rbac group name already exists",
        ) from None
    return RbacGroupRead.model_validate(rbac_group)


def delete_rbac_group(db: Session, group_id: int) -> None:
    rbac_group = repository.get_rbac_group_by_id(db, group_id)
    if rbac_group is None:
        raise HTTPException(status_code=404, detail="Rbac group not found")
    repository.delete_rbac_group(db, rbac_group)