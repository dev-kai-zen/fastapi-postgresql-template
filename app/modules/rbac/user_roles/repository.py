from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timezone import now_app
from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.user_roles.model import RbacUserRoles
from app.modules.rbac.user_roles.schema import RbacUserRoleCreate, RbacUserRoleUpdate


def _user_roles_join_role_select():
    return select(RbacUserRoles, RbacRole).join(
        RbacRole, RbacUserRoles.role_id == RbacRole.id
    )


def list_rbac_user_roles_with_join(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[tuple[RbacUserRoles, RbacRole]]:
    stmt = (
        _user_roles_join_role_select()
        .order_by(RbacUserRoles.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return [(r[0], r[1]) for r in db.execute(stmt).all()]


def list_rbac_user_roles_by_user_ids_with_join(
    db: Session, user_ids: list[int]
) -> list[tuple[RbacUserRoles, RbacRole]]:
    if not user_ids:
        return []
    stmt = (
        _user_roles_join_role_select()
        .where(RbacUserRoles.user_id.in_(user_ids))
        .order_by(RbacUserRoles.id.asc())
    )
    return [(r[0], r[1]) for r in db.execute(stmt).all()]


def list_rbac_user_roles_by_user_id(
    db: Session, user_id: int
) -> list[RbacUserRoles]:
    stmt = (
        select(RbacUserRoles)
        .where(RbacUserRoles.user_id == user_id)
        .order_by(RbacUserRoles.id.asc())
    )
    return list(db.scalars(stmt).all())


def list_rbac_user_roles_by_role_id(
    db: Session, role_id: int
) -> list[RbacUserRoles]:
    stmt = (
        select(RbacUserRoles)
        .where(RbacUserRoles.role_id == role_id)
        .order_by(RbacUserRoles.id.asc())
    )
    return list(db.scalars(stmt).all())


def get_rbac_user_role_by_id(db: Session, user_role_id: int) -> RbacUserRoles | None:
    return db.get(RbacUserRoles, user_role_id)


def get_rbac_user_roles_by_ids(db: Session, ids: list[int]) -> list[RbacUserRoles]:
    return list(
        db.scalars(select(RbacUserRoles).filter(RbacUserRoles.id.in_(ids))).all()
    )


def create_rbac_user_role(
    db: Session, create_data: RbacUserRoleCreate, *, assigned_by: int
) -> RbacUserRoles:
    row = RbacUserRoles(
        user_id=create_data.user_id,
        role_id=create_data.role_id,
        assigned_by=assigned_by,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_rbac_user_role(
    db: Session,
    user_role: RbacUserRoles,
    update_data: RbacUserRoleUpdate,
) -> RbacUserRoles:
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user_role, key, value)
    user_role.updated_at = now_app()
    db.commit()
    db.refresh(user_role)
    return user_role


def delete_rbac_user_role(db: Session, user_role: RbacUserRoles) -> None:
    db.delete(user_role)
    db.commit()
