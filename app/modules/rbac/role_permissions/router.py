"""HTTP routes for role–permission links. Each handler delegates to `service` only."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_access_token_payload
from app.modules.rbac.role_permissions import service
from app.modules.rbac.role_permissions.schema import (
    RbacRolePermissionCreate,
    RbacRolePermissionReadJoined,
    RbacRolePermissionUpdate,
)

router = APIRouter(
    prefix="/rbac/role-permissions",
    tags=["rbac-role-permissions"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacRolePermissionReadJoined])
def list_rbac_role_permissions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RbacRolePermissionReadJoined]:
    return service.list_rbac_role_permissions(db, skip=skip, limit=limit)


@router.get(
    "/by-role-ids",
    response_model=list[RbacRolePermissionReadJoined],
)
def list_rbac_role_permissions_by_role_ids(
    role_ids: list[int] = Query(),
    db: Session = Depends(get_db),
) -> list[RbacRolePermissionReadJoined]:
    return service.list_rbac_role_permissions_by_role_ids(db, role_ids)


@router.get(
    "/role/{role_id}",
    response_model=list[RbacRolePermissionReadJoined],
)
def get_rbac_role_permissions_by_role_id(
    role_id: int, db: Session = Depends(get_db)
) -> list[RbacRolePermissionReadJoined]:
    return service.get_rbac_role_permissions_by_role_id(db, role_id)


@router.post(
    "",
    response_model=RbacRolePermissionReadJoined,
    status_code=status.HTTP_201_CREATED,
)
def create_rbac_role_permissions(
    create_data: RbacRolePermissionCreate, db: Session = Depends(get_db)
) -> RbacRolePermissionReadJoined:
    return service.create_rbac_role_permissions(db, create_data)


@router.patch(
    "/role/{role_id}",
    response_model=list[RbacRolePermissionReadJoined],
)
def update_rbac_role_permissions_by_role_id(
    role_id: int,
    update_data: RbacRolePermissionUpdate,
    db: Session = Depends(get_db),
) -> list[RbacRolePermissionReadJoined]:
    return service.update_rbac_role_permissions_by_role_id(
        db, role_id, update_data
    )
