from sqlalchemy.orm import Session

from app.modules.rbac.role_permissions import queries as role_permissions_queries
from app.modules.rbac.user_roles import service as user_roles_service


class RbacClient:
    """RBAC module boundary (local service today; HTTP later)."""

    def list_permissions_for_role(
        self, db: Session, role_id: int | None
    ) -> list[dict]:
        return role_permissions_queries.list_permission_dicts_for_role(db, role_id)

    def list_permissions_for_user(self, db: Session, user_id: int) -> list[dict]:
        return role_permissions_queries.list_permission_dicts_for_user(db, user_id)

    def get_primary_role_id_for_user(self, db: Session, user_id: int) -> int | None:
        return user_roles_service.get_primary_role_id_for_user(db, user_id)
