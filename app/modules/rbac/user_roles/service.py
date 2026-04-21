from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role.schema import RbacRoleRead
from app.modules.rbac.role_permissions import service as role_permissions_service
from app.modules.rbac.users_client import users_client
from app.modules.rbac.user_roles import repository
from app.modules.rbac.user_roles.model import RbacUserRoles
from app.modules.rbac.role_permissions.schema import RbacRolePermissionReadJoined
from app.modules.rbac.user_roles.schema import (
    RbacUserRoleCreate,
    RbacUserRoleRead,
    RbacUserRoleReadJoined,
    RbacUserRoleReadJoinedWithPermissions,
    RbacUserRoleUpdate,
    RbacUserRoleUserBrief,
)


def _user_ids_for_assignment_rows(
    rows: list[tuple[RbacUserRoles, RbacRole]],
) -> list[int]:
    out: list[int] = []
    for ur, _ in rows:
        out.append(ur.user_id)
        out.append(ur.assigned_by)
    return list(dict.fromkeys(out))


def _to_joined(
    ur: RbacUserRoles,
    role: RbacRole,
    users_map: dict[int, RbacUserRoleUserBrief],
) -> RbacUserRoleReadJoined:
    user = users_map.get(ur.user_id)
    assigned_by_user = users_map.get(ur.assigned_by)
    if user is None or assigned_by_user is None:
        raise HTTPException(
            status_code=500,
            detail="Inconsistent user reference for RBAC user-role assignment",
        )
    return RbacUserRoleReadJoined(
        id=ur.id,
        user_id=ur.user_id,
        role_id=ur.role_id,
        assigned_by=ur.assigned_by,
        assigned_at=ur.assigned_at,
        created_at=ur.created_at,
        updated_at=ur.updated_at,
        user=user,
        role=RbacRoleRead.model_validate(role),
        assigned_by_user=assigned_by_user,
    )


def list_rbac_user_roles(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacUserRoleReadJoined]:
    rows = repository.list_rbac_user_roles_with_join(db, skip=skip, limit=limit)
    users_map = users_client.get_users_by_ids_map(
        db, _user_ids_for_assignment_rows(rows)
    )
    return [_to_joined(ur, role, users_map) for ur, role in rows]


def list_rbac_user_roles_by_user_ids(
    db: Session, user_ids: list[int]
) -> list[RbacUserRoleReadJoinedWithPermissions]:
    rows = repository.list_rbac_user_roles_by_user_ids_with_join(db, user_ids)
    if not rows:
        return []
    users_map = users_client.get_users_by_ids_map(
        db, _user_ids_for_assignment_rows(rows)
    )
    role_ids = list(dict.fromkeys(ur.role_id for ur, _ in rows))
    perms = role_permissions_service.list_rbac_role_permissions_by_role_ids(
        db, role_ids
    )
    by_role: dict[int, list[RbacRolePermissionReadJoined]] = defaultdict(list)
    for p in perms:
        by_role[p.role_id].append(p)
    return [
        RbacUserRoleReadJoinedWithPermissions.model_validate(
            {
                **_to_joined(ur, role, users_map).model_dump(),
                "permissions": list(by_role.get(ur.role_id, [])),
            }
        )
        for ur, role in rows
    ]


def get_rbac_user_roles_by_user_id(
    db: Session, user_id: int
) -> list[RbacUserRoleReadJoinedWithPermissions]:
    return list_rbac_user_roles_by_user_ids(db, [user_id])


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


def get_primary_role_id_for_user(db: Session, user_id: int) -> int | None:
    """First role id from row order (`id` asc), or `None` if no assignments."""
    rows = repository.list_rbac_user_roles_by_user_id(db, user_id)
    return rows[0].role_id if rows else None


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


def create_rbac_user_roles(
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


def update_rbac_user_roles(
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


def delete_rbac_user_roles(db: Session, user_role_id: int) -> None:
    row = repository.get_rbac_user_role_by_id(db, user_role_id)
    if row is None:
        raise HTTPException(
            status_code=404, detail="RBAC user-role assignment not found"
        )
    repository.delete_rbac_user_role(db, row)
