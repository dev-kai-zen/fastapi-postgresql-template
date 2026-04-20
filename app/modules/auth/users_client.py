from sqlalchemy.orm import Session

from app.modules.auth.schema import AuthUserIdentity
from app.modules.users import service as users_service
from app.modules.users.schema import UserGoogleInfo, UserRead


class UsersClient:
    """Calls the users module service boundary (local today; HTTP client later)."""

    def upsert_google_identity(
        self, db: Session, google_userinfo: dict
    ) -> AuthUserIdentity:
        google_user = UserGoogleInfo.model_validate(google_userinfo)
        user_public = users_service.upsert_google_identity(db, google_user)
        return AuthUserIdentity(
            id=user_public.id,
            role_id=user_public.role_id,
            user_claims=user_public.model_dump(mode="json"),
        )

    def get_user(self, db: Session, user_id: int) -> UserRead:
        return users_service.get_user_by_id(db, user_id)
