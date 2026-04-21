from sqlalchemy.orm import Session

from app.modules.users import service as users_service
from app.modules.users.schema import UserGoogleInfo, UserRead


class UsersClient:
    """Calls the users module service boundary (local today; HTTP client later)."""

    def upsert_google_identity(
        self, db: Session, google_userinfo: dict
    ) -> UserRead:
        google_user = UserGoogleInfo.model_validate(google_userinfo)
        return users_service.upsert_google_identity(db, google_user)

    def get_user(self, db: Session, user_id: int) -> UserRead:
        return users_service.get_user_by_id(db, user_id)
