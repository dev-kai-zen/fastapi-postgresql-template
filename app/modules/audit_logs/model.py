from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, JSONB
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from app.core.timezone import now_app


class AuditLog(Base):
    """
    Append-only domain audit trail. Rows are not updated in place; prefer no
    `updated_at` so the table reads as an immutable event stream.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_user_id_created_at", "user_id", "created_at"),
        Index("ix_audit_logs_resource", "resource_type", "resource_id", "created_at"),
        Index("ix_audit_logs_action_created_at", "action", "created_at"),
        Index("ix_audit_logs_request_id", "request_id"),
        Index("ix_audit_logs_tenant_id_created_at", "tenant_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # When the event was recorded (ingestion time). Use for ordering and retention.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=now_app, index=True
    )
    # When the business action actually occurred (e.g. async worker backfill). Defaults to app "now" at write time in the service layer if unset.
    occurred_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    # Who — snapshot + FK. SET NULL keeps history if the user row is removed.
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    actor_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="user",
    )
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)

    # What was done (create, update, delete, read, login, export, etc.)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    # What entity was affected (table name, aggregate, or API resource name)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Which bounded context / module produced the record
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)

    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changed_fields: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # Optional multi-tenant key (String until you add a tenants table)
    tenant_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Where & correlation (HTTP / tracing)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Outcome (security-sensitive actions, failed permission checks, etc.)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Unstructured or provider-specific context (do not use attribute name "metadata" — reserved on Base)
    extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
