from sqlalchemy.orm import Session

from app.modules.users import service as users_service
from app.modules.users.schema import UserGoogleInfo, UserPublic


class UsersClient:
    """Calls the users module service boundary (local today; HTTP client later)."""

    def upsert_google_identity(self, db: Session, data: UserGoogleInfo) -> UserPublic:
        return users_service.upsert_google_identity(db, data)
