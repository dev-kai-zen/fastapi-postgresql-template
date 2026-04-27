from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.modules.audit_logs.model import AuditLog
from app.modules.audit_logs.schema import AuditLogCreate


def _apply_list_filters(
    query,
    *,
    created_at_from: datetime | None,
    created_at_to: datetime | None,
    occurred_at_from: datetime | None,
    occurred_at_to: datetime | None,
    email: str | None,
    action: str | None,
    resource_type: str | None,
    success: bool | None,
):
    conditions: list = []

    if created_at_from is not None:
        conditions.append(AuditLog.created_at >= created_at_from)
    if created_at_to is not None:
        conditions.append(AuditLog.created_at <= created_at_to)

    if occurred_at_from is not None:
        conditions.append(AuditLog.occurred_at >= occurred_at_from)
    if occurred_at_to is not None:
        conditions.append(AuditLog.occurred_at <= occurred_at_to)

    if email is not None:
        term = email.strip()
        if term:
            pattern = f"%{term}%"
            conditions.append(AuditLog.email.ilike(pattern))

    if action is not None and action.strip() != "":
        conditions.append(AuditLog.action == action.strip())
    if resource_type is not None and resource_type.strip() != "":
        conditions.append(AuditLog.resource_type == resource_type.strip())

    if success is not None:
        conditions.append(AuditLog.success == success)

    if conditions:
        return query.where(and_(*conditions))
    return query


def _order_by_clause(*, sort_by: str, sort_order: str):
    column = getattr(AuditLog, sort_by)
    primary = column.desc() if sort_order == "desc" else column.asc()
    if sort_by in ("occurred_at", "email"):
        primary = primary.nulls_last()
    tie = AuditLog.id.desc() if sort_order == "desc" else AuditLog.id.asc()
    return primary, tie


def count_audit_logs(
    db: Session,
    *,
    created_at_from: datetime | None = None,
    created_at_to: datetime | None = None,
    occurred_at_from: datetime | None = None,
    occurred_at_to: datetime | None = None,
    email: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    success: bool | None = None,
) -> int:
    query = select(func.count()).select_from(AuditLog)
    query = _apply_list_filters(
        query,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        occurred_at_from=occurred_at_from,
        occurred_at_to=occurred_at_to,
        email=email,
        action=action,
        resource_type=resource_type,
        success=success,
    )
    return int(db.scalar(query) or 0)


def list_audit_logs(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    created_at_from: datetime | None = None,
    created_at_to: datetime | None = None,
    occurred_at_from: datetime | None = None,
    occurred_at_to: datetime | None = None,
    email: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    success: bool | None = None,
) -> list[AuditLog]:
    query = select(AuditLog)
    query = _apply_list_filters(
        query,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        occurred_at_from=occurred_at_from,
        occurred_at_to=occurred_at_to,
        email=email,
        action=action,
        resource_type=resource_type,
        success=success,
    )
    primary, tie = _order_by_clause(sort_by=sort_by, sort_order=sort_order)
    query = query.order_by(primary, tie).offset(skip).limit(limit)
    return list(db.scalars(query).all())


def get_audit_log_by_id(db: Session, audit_log_id: int) -> AuditLog | None:
    return db.get(AuditLog, audit_log_id)


def create_audit_log(db: Session, data: AuditLogCreate) -> AuditLog:
    row = AuditLog(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
