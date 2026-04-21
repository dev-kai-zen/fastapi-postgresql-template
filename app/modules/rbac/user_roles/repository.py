from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.rbac.role.model import RbacRole
from app.modules.rbac.user_roles.model import RbacUserRoles


def _user_roles_join_role_select():
    return select(RbacUserRoles, RbacRole).join(
        RbacRole, RbacUserRoles.role_id == RbacRole.id
    )


def list_rbac_user_roles(
    db: Session, *, skip: int = 0, limit: int = 100
) -> list[tuple[RbacUserRoles, RbacRole]]:
    stmt = (
        _user_roles_join_role_select()
        .order_by(RbacUserRoles.id.asc())
        .offset(skip)
        .limit(limit)
    )
    return [(r[0], r[1]) for r in db.execute(stmt).all()]


def list_rbac_user_roles_by_user_ids(
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


def set_rbac_user_roles_by_user_id(
    db: Session,
    user_id: int,
    role_ids: list[int],
    *,
    assigned_by: int,
) -> None:
    db.execute(delete(RbacUserRoles).where(RbacUserRoles.user_id == user_id))
    for rid in role_ids:
        db.add(
            RbacUserRoles(
                user_id=user_id,
                role_id=rid,
                assigned_by=assigned_by,
            )
        )
    db.commit()
