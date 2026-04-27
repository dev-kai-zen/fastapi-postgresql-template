from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.audit_logs import repository
from app.modules.audit_logs.schema import (
    AuditLogCreate,
    AuditLogListResponse,
    AuditLogListSortBy,
    AuditLogListSortOrder,
    AuditLogRead,
)


def list_audit_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    sort_by: AuditLogListSortBy = AuditLogListSortBy.CREATED_AT,
    sort_order: AuditLogListSortOrder = AuditLogListSortOrder.DESC,
    created_at_from: datetime | None = None,
    created_at_to: datetime | None = None,
    occurred_at_from: datetime | None = None,
    occurred_at_to: datetime | None = None,
    email: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    success: bool | None = None,
) -> AuditLogListResponse:
    total = repository.count_audit_logs(
        db,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        occurred_at_from=occurred_at_from,
        occurred_at_to=occurred_at_to,
        email=email,
        action=action,
        resource_type=resource_type,
        success=success,
    )
    rows = repository.list_audit_logs(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        occurred_at_from=occurred_at_from,
        occurred_at_to=occurred_at_to,
        email=email,
        action=action,
        resource_type=resource_type,
        success=success,
    )
    return AuditLogListResponse(
        data=[AuditLogRead.model_validate(r) for r in rows],
        total=total,
    )


def create_audit_log(db: Session, data: AuditLogCreate) -> AuditLogRead:
    """Append a single audit row. Other top-level modules should call this via their own `audit_log_client` (see modular monolith rules)."""
    row = repository.create_audit_log(db, data)
    return AuditLogRead.model_validate(row)


def get_audit_log_by_id(db: Session, audit_log_id: int) -> AuditLogRead:
    row = repository.get_audit_log_by_id(db, audit_log_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )
    return AuditLogRead.model_validate(row)
