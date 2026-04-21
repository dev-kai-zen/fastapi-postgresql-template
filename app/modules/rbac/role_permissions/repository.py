from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.rbac.permissions.model import RbacPermission
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role_permissions.model import RbacRolePermissions
from app.modules.rbac.role_permissions.schema import RbacRolePermissionCreate


def _role_permission_joined_select():
    return (
        select(RbacRolePermissions, RbacRole, RbacPermission)
        .join(RbacRole, RbacRolePermissions.role_id == RbacRole.id)
        .join(RbacPermission, RbacRolePermissions.permission_id == RbacPermission.id)
    )


def _rows_joined(
    db: Session, stmt
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    return [(r[0], r[1], r[2]) for r in db.execute(stmt).all()]


def list_rbac_role_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    stmt = (
        _role_permission_joined_select()
        .order_by(RbacRolePermissions.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return _rows_joined(db, stmt)


def list_rbac_role_permissions_by_role_ids(
    db: Session, role_ids: list[int]
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    if not role_ids:
        return []
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.role_id.in_(role_ids))
        .order_by(RbacRolePermissions.id.asc())
    )
    return _rows_joined(db, stmt)


def get_rbac_role_permissions_by_role_id(
    db: Session, role_id: int
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.role_id == role_id)
        .order_by(RbacRolePermissions.id.asc())
    )
    return _rows_joined(db, stmt)


def get_rbac_role_permission_joined_by_link_id(
    db: Session, role_permission_id: int
) -> tuple[RbacRolePermissions, RbacRole, RbacPermission] | None:
    stmt = _role_permission_joined_select().where(
        RbacRolePermissions.id == role_permission_id
    )
    row = db.execute(stmt).first()
    if row is None:
        return None
    return (row[0], row[1], row[2])


def get_rbac_role_permission_by_id(
    db: Session, role_permission_id: int
) -> RbacRolePermissions | None:
    return db.get(RbacRolePermissions, role_permission_id)


def get_rbac_role_permission_by_role_and_permission_id(
    db: Session, role_id: int, permission_id: int
) -> RbacRolePermissions | None:
    stmt = select(RbacRolePermissions).where(
        RbacRolePermissions.role_id == role_id,
        RbacRolePermissions.permission_id == permission_id,
    )
    return db.scalars(stmt).first()


def create_rbac_role_permissions(
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


def update_rbac_role_permissions_by_role_id(
    db: Session, role_id: int, permission_ids: list[int]
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    """Replace all permission rows for `role_id` with `permission_ids` (one transaction)."""
    db.execute(
        delete(RbacRolePermissions).where(RbacRolePermissions.role_id == role_id)
    )
    for pid in permission_ids:
        db.add(RbacRolePermissions(role_id=role_id, permission_id=pid))
    db.commit()
    stmt = (
        _role_permission_joined_select()
        .where(RbacRolePermissions.role_id == role_id)
        .order_by(RbacRolePermissions.id.asc())
    )
    return _rows_joined(db, stmt)


def delete_rbac_role_permissions(
    db: Session, role_permission: RbacRolePermissions
) -> None:
    db.delete(role_permission)
    db.commit()
