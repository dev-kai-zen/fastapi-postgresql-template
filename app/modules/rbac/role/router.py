from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac_codes import RBAC_MANAGE, RBAC_READ
from app.dependencies.rbac_deps import require_permission
from app.dependencies.token_payload_deps import require_access_token_payload
from app.modules.rbac.role import service
from app.modules.rbac.role.schema import RbacRoleCreate, RbacRoleRead, RbacRoleUpdate

router = APIRouter(
    prefix="/rbac/roles",
    tags=["rbac-roles"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacRoleRead])
def list_rbac_roles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> list[RbacRoleRead]:
    return service.list_rbac_roles(db, skip=skip, limit=limit)


@router.get("/get-by-ids", response_model=list[RbacRoleRead])
def list_rbac_roles_by_ids(
    ids: list[int],
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> list[RbacRoleRead]:
    return service.list_rbac_roles_by_ids(db, ids)


@router.get("/{role_id}", response_model=RbacRoleRead)
def get_rbac_role_by_id(
    role_id: int,
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> RbacRoleRead:
    return service.get_rbac_role_by_id(db, role_id)


@router.post("", response_model=RbacRoleRead, status_code=status.HTTP_201_CREATED)
def create_rbac_role(
    create_data: RbacRoleCreate,
    _: None = Depends(require_permission(RBAC_MANAGE)),
    db: Session = Depends(get_db),
) -> RbacRoleRead:
    return service.create_rbac_role(db, create_data)


@router.patch("/{role_id}", response_model=RbacRoleRead)
def update_rbac_role(
    role_id: int,
    update_data: RbacRoleUpdate,
    _: None = Depends(require_permission(RBAC_MANAGE)),
    db: Session = Depends(get_db),
) -> RbacRoleRead:
    return service.update_rbac_role(db, role_id, update_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rbac_role(
    role_id: int,
    _: None = Depends(require_permission(RBAC_MANAGE)),
    db: Session = Depends(get_db),
) -> None:
    service.delete_rbac_role(db, role_id)
