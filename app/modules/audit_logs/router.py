from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.rbac_codes import AUDIT_LOG_READ
from app.dependencies.rbac_deps import require_permission
from app.dependencies.token_payload_deps import require_access_token_payload
from app.modules.audit_logs import service
from app.modules.audit_logs.schema import (
    AuditLogListResponse,
    AuditLogListSortBy,
    AuditLogListSortOrder,
    AuditLogRead,
)

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit-logs"],
    dependencies=[Depends(require_access_token_payload)],
)


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
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
    _: None = Depends(require_permission(AUDIT_LOG_READ)),
    db: Session = Depends(get_db),
) -> AuditLogListResponse:
    return service.list_audit_logs(
        db,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        occurred_at_from=occurred_at_from,
        occurred_at_to=occurred_at_to,
        email=email,
        action=action,
        resource_type=resource_type,
        success=success,
    )


@router.get("/{audit_log_id}", response_model=AuditLogRead)
def get_audit_log_by_id(
    audit_log_id: int,
    _: None = Depends(require_permission(AUDIT_LOG_READ)),
    db: Session = Depends(get_db),
) -> AuditLogRead:
    return service.get_audit_log_by_id(db, audit_log_id)
