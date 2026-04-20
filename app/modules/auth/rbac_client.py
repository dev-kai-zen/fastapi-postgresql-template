from sqlalchemy.orm import Session

from app.modules.rbac.role_permissions import service as role_permissions_service


class RbacClient:
    """RBAC module boundary (local service today; HTTP later)."""

    def list_permissions_for_role(
        self, db: Session, role_id: int | None
    ) -> list[dict]:
        return role_permissions_service.list_permission_dicts_for_role(db, role_id)
