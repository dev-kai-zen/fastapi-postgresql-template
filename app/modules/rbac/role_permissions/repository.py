from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.rbac.permissions.model import RbacPermission
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role_permissions.model import RbacRolePermissions


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


def _delete_rbac_role_permissions_for_role_id(db: Session, role_id: int) -> None:
    db.execute(
        delete(RbacRolePermissions).where(RbacRolePermissions.role_id == role_id)
    )


def _insert_rbac_role_permission_rows(
    db: Session, role_id: int, permission_ids: list[int]
) -> None:
    for pid in permission_ids:
        db.add(RbacRolePermissions(role_id=role_id, permission_id=pid))


def set_rbac_role_permissions_by_role_id(
    db: Session, role_id: int, permission_ids: list[int]
) -> list[tuple[RbacRolePermissions, RbacRole, RbacPermission]]:
    """Delete all links for `role_id`, then insert `permission_ids` (one transaction)."""
    _delete_rbac_role_permissions_for_role_id(db, role_id)
    db.flush()
    _insert_rbac_role_permission_rows(db, role_id, permission_ids)
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
