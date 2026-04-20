from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_access_token_payload
from app.modules.rbac.permissions import service
from app.modules.rbac.permissions.schema import (
    RbacPermissionCreate,
    RbacPermissionRead,
    RbacPermissionUpdate,
)

router = APIRouter(
    prefix="/rbac/permissions",
    tags=["rbac-permissions"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacPermissionRead])
def list_rbac_permissions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RbacPermissionRead]:
    return service.list_rbac_permissions(db, skip=skip, limit=limit)


@router.get("/get-by-ids", response_model=list[RbacPermissionRead])
def get_rbac_permissions_by_ids(
    ids: list[int], db: Session = Depends(get_db)
) -> list[RbacPermissionRead]:
    return service.get_rbac_permissions_by_ids(db, ids)


@router.get("/{permission_id}", response_model=RbacPermissionRead)
def get_rbac_permission_by_id(
    permission_id: int, db: Session = Depends(get_db)
) -> RbacPermissionRead:
    return service.get_rbac_permission_by_id(db, permission_id)


@router.post("", response_model=RbacPermissionRead, status_code=status.HTTP_201_CREATED)
def create_rbac_permission(
    create_data: RbacPermissionCreate, db: Session = Depends(get_db)
) -> RbacPermissionRead:
    return service.create_rbac_permission(db, create_data)


@router.patch("/{permission_id}", response_model=RbacPermissionRead)
def update_rbac_permission(
    permission_id: int,
    update_data: RbacPermissionUpdate,
    db: Session = Depends(get_db),
) -> RbacPermissionRead:
    return service.update_rbac_permission(db, permission_id, update_data)


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rbac_permission(
    permission_id: int, db: Session = Depends(get_db)
) -> None:
    service.delete_rbac_permission(db, permission_id)
