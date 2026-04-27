from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac_codes import RBAC_MANAGE, RBAC_READ
from app.dependencies.rbac_deps import require_permission
from app.dependencies.token_payload_deps import require_access_token_payload, require_current_user_id
from app.modules.rbac.user_roles import service
from app.modules.rbac.user_roles.schema import (
    RbacUserRolesDetailByUserId,
    RbacUserRolesForUserId,
    RbacUserRolesListItemWithUser,
    RbacUserRoleUpdateByUserId,
)

router = APIRouter(
    prefix="/rbac/user-roles",
    tags=["rbac-user-roles"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacUserRolesListItemWithUser])
def list_rbac_user_roles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> list[RbacUserRolesListItemWithUser]:
    return service.list_rbac_user_roles(db, skip=skip, limit=limit)


@router.get(
    "/by-user-ids",
    response_model=list[RbacUserRolesForUserId],
)
def list_rbac_user_roles_by_user_ids(
    user_ids: list[int] = Query(),
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> list[RbacUserRolesForUserId]:
    return service.list_rbac_user_roles_by_user_ids(db, user_ids)


@router.get(
    "/user/{user_id}",
    response_model=RbacUserRolesDetailByUserId,
)
def get_rbac_user_roles_permissions_by_user_id(
    user_id: int,
    _: None = Depends(require_permission(RBAC_READ)),
    db: Session = Depends(get_db),
) -> RbacUserRolesDetailByUserId:
    return service.get_rbac_user_roles_permissions_by_user_id(db, user_id)


@router.patch(
    "/user/{user_id}",
    response_model=RbacUserRolesDetailByUserId,
)
def set_rbac_user_roles_by_user_id(
    user_id: int,
    update_data: RbacUserRoleUpdateByUserId,
    _: None = Depends(require_permission(RBAC_MANAGE)),
    db: Session = Depends(get_db),
    assigned_by: int = Depends(require_current_user_id),
) -> RbacUserRolesDetailByUserId:
    return service.set_rbac_user_roles_by_user_id(
        db, user_id, update_data, assigned_by=assigned_by
    )
