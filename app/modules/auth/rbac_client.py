from sqlalchemy.orm import Session

from app.modules.rbac.role_permissions import service as role_permissions_service
from app.modules.rbac.user_roles import service as user_roles_service
from app.modules.rbac.user_roles.schema import RbacUserRolesDetailByUserId


class RbacClient:
    """RBAC module boundary (local service today; HTTP later)."""

    def get_rbac_user_roles_permissions_by_user_id(self, db: Session, user_id: int) -> RbacUserRolesDetailByUserId:
        return user_roles_service.get_rbac_user_roles_permissions_by_user_id(db, user_id)

    def get_primary_role_id_for_user(self, db: Session, user_id: int) -> int | None:
        return user_roles_service.get_primary_role_id_for_user(db, user_id)
