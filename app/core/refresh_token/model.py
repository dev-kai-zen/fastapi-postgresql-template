from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timezone import now_app
from app.models.base import Base


class AuthRefreshToken(Base):
    """Server-side record for issued refresh JWTs (by ``jti``); revocation sets ``revoked_at``."""

    __tablename__ = "auth_refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app
    )
