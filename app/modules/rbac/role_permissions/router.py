from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_access_token_payload
from app.modules.rbac.role_permissions import service
from app.modules.rbac.role_permissions.schema import (
    RbacRolePermissionCreate,
    RbacRolePermissionRead,
    RbacRolePermissionUpdate,
)

router = APIRouter(
    prefix="/rbac/role-permissions",
    tags=["rbac-role-permissions"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacRolePermissionRead])
def list_rbac_role_permissions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RbacRolePermissionRead]:
    return service.list_rbac_role_permissions(db, skip=skip, limit=limit)


@router.get("/get-by-ids", response_model=list[RbacRolePermissionRead])
def get_rbac_role_permissions_by_ids(
    ids: list[int], db: Session = Depends(get_db)
) -> list[RbacRolePermissionRead]:
    return service.get_rbac_role_permissions_by_ids(db, ids)


@router.get("/{role_permission_id}", response_model=RbacRolePermissionRead)
def get_rbac_role_permission_by_id(
    role_permission_id: int, db: Session = Depends(get_db)
) -> RbacRolePermissionRead:
    return service.get_rbac_role_permission_by_id(db, role_permission_id)


@router.post(
    "",
    response_model=RbacRolePermissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rbac_role_permission(
    create_data: RbacRolePermissionCreate, db: Session = Depends(get_db)
) -> RbacRolePermissionRead:
    return service.create_rbac_role_permission(db, create_data)


@router.patch("/{role_permission_id}", response_model=RbacRolePermissionRead)
def update_rbac_role_permission(
    role_permission_id: int,
    update_data: RbacRolePermissionUpdate,
    db: Session = Depends(get_db),
) -> RbacRolePermissionRead:
    return service.update_rbac_role_permission(
        db, role_permission_id, update_data
    )


@router.delete("/{role_permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rbac_role_permission(
    role_permission_id: int, db: Session = Depends(get_db)
) -> None:
    service.delete_rbac_role_permission(db, role_permission_id)
