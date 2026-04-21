from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_access_token_payload, require_current_user_id
from app.modules.rbac.user_roles import service
from app.modules.rbac.user_roles.schema import (
    RbacUserRoleCreate,
    RbacUserRoleRead,
    RbacUserRoleUpdate,
)

router = APIRouter(
    prefix="/rbac/user-roles",
    tags=["rbac-user-roles"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=list[RbacUserRoleRead])
def list_rbac_user_roles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[RbacUserRoleRead]:
    return service.list_rbac_user_roles(db, skip=skip, limit=limit)


@router.get("/get-by-ids", response_model=list[RbacUserRoleRead])
def get_rbac_user_roles_by_ids(
    ids: list[int], db: Session = Depends(get_db)
) -> list[RbacUserRoleRead]:
    return service.get_rbac_user_roles_by_ids(db, ids)


@router.get("/by-user/{user_id}", response_model=list[RbacUserRoleRead])
def list_rbac_user_roles_by_user_id(
    user_id: int, db: Session = Depends(get_db)
) -> list[RbacUserRoleRead]:
    return service.list_rbac_user_roles_by_user_id(db, user_id)


@router.get("/by-role/{role_id}", response_model=list[RbacUserRoleRead])
def list_rbac_user_roles_by_role_id(
    role_id: int, db: Session = Depends(get_db)
) -> list[RbacUserRoleRead]:
    return service.list_rbac_user_roles_by_role_id(db, role_id)


@router.get("/{user_role_id}", response_model=RbacUserRoleRead)
def get_rbac_user_role_by_id(
    user_role_id: int, db: Session = Depends(get_db)
) -> RbacUserRoleRead:
    return service.get_rbac_user_role_by_id(db, user_role_id)


@router.post(
    "",
    response_model=RbacUserRoleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_rbac_user_role(
    create_data: RbacUserRoleCreate,
    db: Session = Depends(get_db),
    assigned_by: int = Depends(require_current_user_id),
) -> RbacUserRoleRead:
    return service.create_rbac_user_role(
        db, create_data, assigned_by=assigned_by
    )


@router.patch("/{user_role_id}", response_model=RbacUserRoleRead)
def update_rbac_user_role(
    user_role_id: int,
    update_data: RbacUserRoleUpdate,
    db: Session = Depends(get_db),
) -> RbacUserRoleRead:
    return service.update_rbac_user_role(db, user_role_id, update_data)


@router.delete("/{user_role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rbac_user_role(
    user_role_id: int, db: Session = Depends(get_db)
) -> None:
    service.delete_rbac_user_role(db, user_role_id)
