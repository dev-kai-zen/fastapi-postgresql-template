from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.rbac.permissions.model import RbacPermission
from app.modules.rbac.permissions.schema import RbacPermissionCreate, RbacPermissionUpdate


def list_rbac_permissions(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacPermission]:
    select_statement = (
        select(RbacPermission)
        .order_by(RbacPermission.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(select_statement).all())


def get_rbac_permission_by_id(db: Session, permission_id: int) -> RbacPermission | None:
    return db.get(RbacPermission, permission_id)


def get_rbac_permissions_by_ids(db: Session, ids: list[int]) -> list[RbacPermission]:
    return list(
        db.scalars(select(RbacPermission).filter(RbacPermission.id.in_(ids))).all()
    )


def create_rbac_permission(
    db: Session, create_data: RbacPermissionCreate
) -> RbacPermission:
    rbac_permission = RbacPermission(
        name=create_data.name,
        description=create_data.description,
        group_id=create_data.group_id,
    )
    db.add(rbac_permission)
    db.commit()
    db.refresh(rbac_permission)
    return rbac_permission


def update_rbac_permission(
    db: Session, rbac_permission: RbacPermission, update_data: RbacPermissionUpdate
) -> RbacPermission:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(rbac_permission, key, value)
    rbac_permission.updated_at = now_app()
    db.commit()
    db.refresh(rbac_permission)
    return rbac_permission


def delete_rbac_permission(db: Session, rbac_permission: RbacPermission) -> None:
    db.delete(rbac_permission)
    db.commit()
