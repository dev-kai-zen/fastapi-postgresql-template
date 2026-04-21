from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from app.core.timezone import now_app


class RbacUserRoles(Base):
    __tablename__ = "rbac_user_roles"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_rbac_user_roles_one_assignment_per_user_and_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("rbac_roles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    assigned_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=now_app,
        onupdate=now_app,
    )
