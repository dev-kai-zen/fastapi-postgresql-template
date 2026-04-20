from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import require_access_token_payload

from app.modules.rbac.group.schema import RbacGroupRead, RbacGroupCreate, RbacGroupUpdate

from app.modules.rbac.group import service


router = APIRouter(
    prefix="/rbac/groups", tags=["rbac-groups"], dependencies=[Depends(require_access_token_payload)])


@router.get("", response_model=list[RbacGroupRead])
def list_rbac_groups(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RbacGroupRead]:
    return service.list_rbac_groups(db, skip=skip, limit=limit)


@router.get("/get-by-ids", response_model=list[RbacGroupRead])
def get_rbac_group_by_ids(ids: list[int], db: Session = Depends(get_db)) -> list[RbacGroupRead]:
    return service.get_rbac_group_by_ids(db, ids)


@router.get("/{group_id}", response_model=RbacGroupRead)
def get_rbac_group_by_id(group_id: int, db: Session = Depends(get_db)) -> RbacGroupRead:
    return service.get_rbac_group_by_id(db, group_id)


@router.post("", response_model=RbacGroupRead, status_code=status.HTTP_201_CREATED)
def create_rbac_group(create_data: RbacGroupCreate, db: Session = Depends(get_db)) -> RbacGroupRead:
    return service.create_rbac_group(db, create_data)


@router.patch("/{group_id}", response_model=RbacGroupRead)
def update_rbac_group(group_id: int, update_data: RbacGroupUpdate, db: Session = Depends(get_db)) -> RbacGroupRead:
    return service.update_rbac_group(db, group_id, update_data)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rbac_group(group_id: int, db: Session = Depends(get_db)) -> None:
    service.delete_rbac_group(db, group_id)
