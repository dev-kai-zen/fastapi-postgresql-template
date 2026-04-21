from sqlalchemy.orm import Session

from app.modules.rbac.role import service as role_service
from app.modules.rbac.role.schema import RbacRoleRead
from app.modules.rbac.role_permissions import service as role_permissions_service
from app.modules.rbac.role_permissions.schema import RbacRolePermissionReadJoined
from app.modules.rbac.user_roles import service as user_roles_service
from app.modules.rbac.user_roles.schema import RbacUserRoleRead


class RbacClient:
    """RBAC module boundary (local service today; HTTP later)."""

    def list_rbac_user_roles_by_user_id(
        self, db: Session, user_id: int
    ) -> list[RbacUserRoleRead]:
        return user_roles_service.list_rbac_user_roles_by_user_id(db, user_id)

    def list_rbac_roles_by_ids(
        self, db: Session, ids: list[int]
    ) -> list[RbacRoleRead]:
        return role_service.list_rbac_roles_by_ids(db, ids)

    def list_rbac_role_permissions_by_ids(
        self, db: Session, ids: list[int]
    ) -> list[RbacRolePermissionReadJoined]:
        return role_permissions_service.list_rbac_role_permissions_by_ids(db, ids)

    def list_rbac_role_permissions_by_role_ids(
        self, db: Session, role_ids: list[int]
    ) -> list[RbacRolePermissionReadJoined]:
        return role_permissions_service.list_rbac_role_permissions_by_role_ids(
            db, role_ids
        )
