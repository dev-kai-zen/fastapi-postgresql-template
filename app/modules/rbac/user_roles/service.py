from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role.schema import RbacRoleRead
from app.modules.rbac.role_permissions import service as role_permissions_service
from app.modules.rbac.role_permissions.schema import RbacRolePermissionReadJoined
from app.modules.rbac.users_client import users_client
from app.modules.rbac.user_roles import repository
from app.modules.rbac.user_roles.model import RbacUserRoles
from app.modules.rbac.user_roles.schema import (
    RbacUserRoleRead,
    RbacUserRoleUpdateByUserId,
    RbacUserRolesDetailByUserId,
    RbacUserRolesForUserId,
    RbacUserRolesListItemWithUser,
)


def _roles_by_user_id_ordered(
    rows: list[tuple[RbacUserRoles, RbacRole]],
) -> dict[int, list[RbacRole]]:
    by_user: dict[int, list[RbacRole]] = defaultdict(list)
    seen_pair: set[tuple[int, int]] = set()
    for ur, role in rows:
        key = (ur.user_id, role.id)
        if key not in seen_pair:
            seen_pair.add(key)
            by_user[ur.user_id].append(role)
    return by_user


def _unique_role_permissions_by_permission_id(
    items: list[RbacRolePermissionReadJoined],
) -> list[RbacRolePermissionReadJoined]:
    seen: set[int] = set()
    out: list[RbacRolePermissionReadJoined] = []
    for p in items:
        if p.permission_id not in seen:
            seen.add(p.permission_id)
            out.append(p)
    return out


def list_rbac_user_roles(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacUserRolesListItemWithUser]:
    rows = repository.list_rbac_user_roles(db, skip=skip, limit=limit)
    if not rows:
        return []
    user_ids_order: list[int] = []
    seen_u: set[int] = set()
    for ur, _ in rows:
        if ur.user_id not in seen_u:
            seen_u.add(ur.user_id)
            user_ids_order.append(ur.user_id)
    roles_by_user = _roles_by_user_id_ordered(rows)
    users_map = users_client.get_users_by_ids_map(db, user_ids_order)
    out: list[RbacUserRolesListItemWithUser] = []
    for uid in user_ids_order:
        user = users_map.get(uid)
        if user is None:
            raise HTTPException(
                status_code=500,
                detail="Inconsistent user reference for RBAC user-role assignment",
            )
        roles = roles_by_user.get(uid, [])
        out.append(
            RbacUserRolesListItemWithUser(
                user=user,
                roles=[RbacRoleRead.model_validate(r) for r in roles],
            )
        )
    return out


def list_rbac_user_roles_by_user_ids(
    db: Session, user_ids: list[int]
) -> list[RbacUserRolesForUserId]:
    if not user_ids:
        return []
    users_map = users_client.get_users_by_ids_map(db, user_ids)
    missing = [uid for uid in user_ids if uid not in users_map]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"User(s) not found: {missing}",
        )
    rows = repository.list_rbac_user_roles_by_user_ids(db, user_ids)
    by_user = _roles_by_user_id_ordered(rows)
    return [
        RbacUserRolesForUserId(
            user_id=uid,
            roles=[RbacRoleRead.model_validate(r) for r in by_user.get(uid, [])],
        )
        for uid in user_ids
    ]


def get_rbac_user_roles_permissions_by_user_id(
    db: Session, user_id: int
) -> RbacUserRolesDetailByUserId:
    users_map = users_client.get_users_by_ids_map(db, [user_id])
    if user_id not in users_map:
        raise HTTPException(status_code=404, detail="User not found")
    rows = repository.list_rbac_user_roles_by_user_ids(db, [user_id])
    roles_list = _roles_by_user_id_ordered(rows).get(user_id, [])
    roles_read = [RbacRoleRead.model_validate(r) for r in roles_list]
    role_ids = [r.id for r in roles_list]
    perms = (
        role_permissions_service.list_rbac_role_permissions_by_role_ids(db, role_ids)
        if role_ids
        else []
    )
    unique_perms = _unique_role_permissions_by_permission_id(perms)
    return RbacUserRolesDetailByUserId(
        user_id=user_id,
        roles=roles_read,
        role_permissions=unique_perms,
    )


def list_rbac_user_roles_by_user_id(
    db: Session, user_id: int
) -> list[RbacUserRoleRead]:
    rows = repository.list_rbac_user_roles_by_user_id(db, user_id)
    return [RbacUserRoleRead.model_validate(row) for row in rows]


def get_primary_role_id_for_user(db: Session, user_id: int) -> int | None:
    """First role id from row order (`id` asc), or `None` if no assignments."""
    rows = repository.list_rbac_user_roles_by_user_id(db, user_id)
    return rows[0].role_id if rows else None


def set_rbac_user_roles_by_user_id(
    db: Session,
    user_id: int,
    update_data: RbacUserRoleUpdateByUserId,
    *,
    assigned_by: int,
) -> RbacUserRolesDetailByUserId:
    users_map = users_client.get_users_by_ids_map(db, [user_id])
    if user_id not in users_map:
        raise HTTPException(status_code=404, detail="User not found")
    role_ids = list(dict.fromkeys(update_data.role_ids))
    try:
        repository.set_rbac_user_roles_by_user_id(
            db, user_id, role_ids, assigned_by=assigned_by
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=(
                "User-role set conflicts (duplicate role or invalid role reference)"
            ),
        ) from None
    return get_rbac_user_roles_permissions_by_user_id(db, user_id)
