from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.token_payload_deps import require_current_user_id
from app.modules.rbac import rbac_guards


def require_permission(
    *codes: str, mode: str = "any"
) -> Callable[..., None]:
    """Depends factory: 403 unless JWT user has the given permission code(s)."""

    def _check(
        user_id: int = Depends(require_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        rbac_guards.permission_guard(user_id, db, list(codes), mode=mode)

    return _check


def require_role(
    *role_names: str, mode: str = "any"
) -> Callable[..., None]:
    """Depends factory: 403 unless JWT user has the given role name(s)."""

    def _check(
        user_id: int = Depends(require_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        rbac_guards.role_guard(user_id, db, list(role_names), mode=mode)

    return _check
