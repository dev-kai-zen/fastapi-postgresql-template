from sqlalchemy.orm import Session
from app.modules.rbac.group.model import RbacGroup
from sqlalchemy import select

from app.modules.rbac.group.schema import RbacGroupCreate, RbacGroupUpdate

from app.core.timezone import now_app


def list_rbac_groups(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacGroup]:
    select_statement = (
        select(RbacGroup)
        .order_by(RbacGroup.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(select_statement).all())


def get_rbac_group_by_id(db: Session, group_id: int) -> RbacGroup | None:
    return db.get(RbacGroup, group_id)


def get_rbac_group_by_ids(db: Session, ids: list[int]) -> list[RbacGroup]:
    return list(db.scalars(select(RbacGroup).filter(RbacGroup.id.in_(ids))).all())


def create_rbac_group(db: Session, create_data: RbacGroupCreate) -> RbacGroup:
    rbac_group = RbacGroup(name=create_data.name)
    db.add(rbac_group)
    db.commit()
    db.refresh(rbac_group)
    return rbac_group


def update_rbac_group(
    db: Session, rbac_group: RbacGroup, update_data: RbacGroupUpdate
) -> RbacGroup:
    if update_data.name is not None:
        rbac_group.name = update_data.name
    rbac_group.updated_at = now_app()
    db.commit()
    db.refresh(rbac_group)
    return rbac_group


def delete_rbac_group(db: Session, rbac_group: RbacGroup) -> None:
    db.delete(rbac_group)
    db.commit()
