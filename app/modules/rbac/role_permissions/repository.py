from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.rbac.role_permissions.model import RbacRolePermissions
from app.modules.rbac.role_permissions.schema import (
    RbacRolePermissionCreate,
    RbacRolePermissionUpdate,
)


def list_rbac_role_permissions(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[RbacRolePermissions]:
    stmt = (
        select(RbacRolePermissions)
        .order_by(RbacRolePermissions.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_rbac_role_permission_by_id(
    db: Session, role_permission_id: int
) -> RbacRolePermissions | None:
    return db.get(RbacRolePermissions, role_permission_id)


def get_rbac_role_permissions_by_ids(
    db: Session, ids: list[int]
) -> list[RbacRolePermissions]:
    return list(
        db.scalars(
            select(RbacRolePermissions).filter(RbacRolePermissions.id.in_(ids))
        ).all()
    )


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
