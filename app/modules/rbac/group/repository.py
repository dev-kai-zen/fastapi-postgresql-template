from sqlalchemy.orm import Session
from app.modules.rbac.group.model import RbacGroup
from sqlalchemy import select



def list_rbac_groups(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacGroup]:
    select_statement = (
        select(RbacGroup)
        .order_by(RbacGroup.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(select_statement).all())