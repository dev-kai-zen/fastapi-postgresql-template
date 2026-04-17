"""Public contract for the users module (other modules depend on this, not on ORM or repository)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class UserPublic:
    """DTO exposed across module boundaries (no SQLAlchemy types)."""

    id: int
    google_id: str
    email: str
    name: str
    picture: str | None
    id_number: str | None
    role_id: int | None
    flags: Any | None
    is_active: int
    last_logged_in: datetime | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class UsersPort(Protocol):
    """Application port for user persistence — implemented inside the users module."""

    def get_by_id(self, db: Session, user_id: int) -> UserPublic | None: ...

    def get_by_google_id(self, db: Session, google_id: str) -> UserPublic | None: ...

    def upsert_google_identity(
        self,
        db: Session,
        *,
        google_id: str,
        email: str,
        name: str,
        picture: str | None,
        last_logged_in: datetime,
    ) -> UserPublic: ...


_users_port_singleton: UsersPort | None = None


def default_users_port() -> UsersPort:
    """Lazily construct the default port implementation (avoids import cycles)."""
    global _users_port_singleton
    if _users_port_singleton is None:
        from app.modules.users.port_adapter import SqlAlchemyUsersPort

        _users_port_singleton = SqlAlchemyUsersPort()
    return _users_port_singleton
