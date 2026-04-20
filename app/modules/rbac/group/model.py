from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from app.core.timezone import now_app


class RbacGroup(Base):
    __tablename__ = "rbac_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_app,
        onupdate=now_app,
    )