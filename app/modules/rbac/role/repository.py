from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.role.schema import RbacRoleCreate, RbacRoleUpdate


def list_rbac_roles(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacRole]:
    stmt = (
        select(RbacRole).order_by(RbacRole.id.asc()).offset(skip).limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_rbac_role_by_id(db: Session, role_id: int) -> RbacRole | None:
    return db.get(RbacRole, role_id)


def list_rbac_roles_by_ids(db: Session, ids: list[int]) -> list[RbacRole]:
    return list(db.scalars(select(RbacRole).filter(RbacRole.id.in_(ids))).all())


def create_rbac_role(db: Session, create_data: RbacRoleCreate) -> RbacRole:
    rbac_role = RbacRole(name=create_data.name, description=create_data.description)
    db.add(rbac_role)
    db.commit()
    db.refresh(rbac_role)
    return rbac_role


def update_rbac_role(
    db: Session, rbac_role: RbacRole, update_data: RbacRoleUpdate
) -> RbacRole:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(rbac_role, key, value)
    rbac_role.updated_at = now_app()
    db.commit()
    db.refresh(rbac_role)
    return rbac_role


def delete_rbac_role(db: Session, rbac_role: RbacRole) -> None:
    db.delete(rbac_role)
    db.commit()
