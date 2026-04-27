from sqlalchemy.orm import Session
from app.modules.audit_logs.schema import AuditLogCreate, AuditLogRead
from app.modules.audit_logs import service as audit_logs_service


class AuditLogClient:
    """Calls the audit logs module service boundary (local today; HTTP client later)."""

    def create_audit_log(self, db: Session, data: AuditLogCreate) -> AuditLogRead:
        return audit_logs_service.create_audit_log(db, data)