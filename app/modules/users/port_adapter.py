"""Default ``UsersPort`` implementation (SQLAlchemy + internal repository)."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.users import repository
from app.modules.users.interface import UserPublic
from app.modules.users.model import User
from app.modules.users.schema import UserCreate


def _to_public(row: User) -> UserPublic:
    return UserPublic(
        id=row.id,
        google_id=row.google_id,
        email=row.email,
        name=row.name,
        picture=row.picture,
        id_number=row.id_number,
        role_id=row.role_id,
        flags=row.flags,
        is_active=row.is_active,
        last_logged_in=row.last_logged_in,
        created_at=row.created_at,
        updated_at=row.updated_at,
        deleted_at=row.deleted_at,
    )


class SqlAlchemyUsersPort:
    def get_by_id(self, db: Session, user_id: int) -> UserPublic | None:
        row = repository.get_user(db, user_id)
        return _to_public(row) if row is not None else None

    def get_by_google_id(self, db: Session, google_id: str) -> UserPublic | None:
        row = repository.get_user_by_google_id(db, google_id)
        return _to_public(row) if row is not None else None

    def upsert_google_identity(
        self,
        db: Session,
        *,
        google_id: str,
        email: str,
        name: str,
        picture: str | None,
        last_logged_in: datetime,
    ) -> UserPublic:
        existing = repository.get_user_by_google_id(db, google_id)
        if existing is not None:
            existing.email = email
            existing.name = name
            existing.picture = picture
            existing.last_logged_in = last_logged_in
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return _to_public(existing)

        obj = UserCreate(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            last_logged_in=last_logged_in,
        )
        created = repository.create_user(db, obj)
        return _to_public(created)
