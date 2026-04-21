"""Inbound boundary to the users module (local `users.service` today; HTTP later)."""

from sqlalchemy.orm import Session

from app.modules.users import service as users_service

from app.modules.rbac.user_roles.schema import RbacUserRoleUserBrief


class UsersClient:
    def get_users_by_ids_map(
        self, db: Session, ids: list[int]
    ) -> dict[int, RbacUserRoleUserBrief]:
        if not ids:
            return {}
        users = users_service.get_users_by_ids(db, ids)
        return {
            u.id: RbacUserRoleUserBrief(
                id=u.id,
                email=u.email,
                first_name=u.first_name,
                last_name=u.last_name,
                picture=u.picture,
            )
            for u in users
        }


users_client = UsersClient()
