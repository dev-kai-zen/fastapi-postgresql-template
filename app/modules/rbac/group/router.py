from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.deps import require_access_token_payload

from app.modules.rbac.group.schema import RbacGroupRead

from app.modules.rbac.group import service


router = APIRouter(
    prefix="/rbac/groups", tags=["rbac-groups"], dependencies=[Depends(require_access_token_payload)])


@router.get("", response_model=list[RbacGroupRead])
def list_rbac_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[RbacGroupRead]:
    return service.list_rbac_groups(db, skip=skip, limit=limit)