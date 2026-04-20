from sqlalchemy.orm import Session
from app.modules.rbac.group.schema import RbacGroupRead
from app.modules.rbac.group import repository


def list_rbac_groups(db: Session, *, skip: int = 0, limit: int = 100) -> list[RbacGroupRead]:
    rbac_groups = repository.list_rbac_groups(db, skip=skip, limit=limit)
    return [RbacGroupRead.model_validate(rbac_group) for rbac_group in rbac_groups]