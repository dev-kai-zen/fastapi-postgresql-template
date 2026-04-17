from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from app.core.timezone import now_utc


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(320))
    name: Mapped[str] = mapped_column(String(255))
    picture: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    id_number: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True)
    role_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    flags: Mapped[Any | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    last_logged_in: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_utc,
        onupdate=now_utc,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
