from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from app.core.timezone import now_app


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), index=True)
    picture: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    id_number: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True)
    role_id: Mapped[int | None] = mapped_column(
        ForeignKey("rbac_roles.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    flags: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"), index=True
    )
    last_logged_in: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_app,
        onupdate=now_app,
    )
