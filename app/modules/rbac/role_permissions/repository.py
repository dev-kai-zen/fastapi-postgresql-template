from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.rbac.permissions.model import RbacPermission
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role_permissions.model import RbacRolePermissions
from app.modules.rbac.role_permissions.schema import (
    RbacRolePermissionCreate,
    RbacRolePermissionUpdate,
)


def _role_permission_joined_select():
    return (
        select(RbacRolePermissions, RbacRole, RbacPermission)
        .join(RbacRole, RbacRolePermissions.role_id == RbacRole.id)
        .join(RbacPermission, RbacRolePermissions.permission_id == RbacPermission.id)
    )


def list_rbac_role_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    stmt = (
        _role_permission_joined_select()
        .order_by(RbacRolePermissions.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return [(r[0], r[1], r[2]) for r in db.execute(stmt).all()]


def get_rbac_role_permission_by_id(
    db: Session, role_permission_id: int
) -> RbacRolePermissions | None:
    return db.get(RbacRolePermissions, role_permission_id)


def get_rbac_role_permission_by_id_with_join(
    db: Session, role_permission_id: int
) -> tuple[RbacRolePermissions, RbacRole, RbacPermission] | None:
    stmt = _role_permission_joined_select().where(
        RbacRolePermissions.id == role_permission_id
    )
    row = db.execute(stmt).first()
    if row is None:
        return None
    return (row[0], row[1], row[2])


def list_rbac_role_permissions_by_ids_with_join(
    db: Session, ids: list[int]
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    if not ids:
        return []
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.id.in_(ids))
        .order_by(RbacRolePermissions.id.asc())
    )
    return [(r[0], r[1], r[2]) for r in db.execute(stmt).all()]


def list_rbac_role_permissions_by_role_ids_with_join(
    db: Session, role_ids: list[int]
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    if not role_ids:
        return []
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.role_id.in_(role_ids))
        .order_by(RbacRolePermissions.id.asc())
    )
    return [(r[0], r[1], r[2]) for r in db.execute(stmt).all()]


def list_rbac_role_permissions_by_role_id_with_join(
    db: Session, role_id: int
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.role_id == role_id)
        .order_by(RbacRolePermissions.id.asc())
    )
    return [(r[0], r[1], r[2]) for r in db.execute(stmt).all()]


def create_rbac_role_permission(
    db: Session, create_data: RbacRolePermissionCreate
) -> RbacRolePermissions:
    row = RbacRolePermissions(
        role_id=create_data.role_id,
        permission_id=create_data.permission_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_rbac_role_permission(
    db: Session,
    role_permission: RbacRolePermissions,
    update_data: RbacRolePermissionUpdate,
) -> RbacRolePermissions:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(role_permission, key, value)
    role_permission.updated_at = now_app()
    db.commit()
    db.refresh(role_permission)
    return role_permission


def delete_rbac_role_permission(
    db: Session, role_permission: RbacRolePermissions
) -> None:
    db.delete(role_permission)
    db.commit()
