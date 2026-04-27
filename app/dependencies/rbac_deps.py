from collections.abc import Awaitable, Callable

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.dependencies.rbac_client import RbacClient
from app.dependencies.token_payload_deps import require_current_user_id

_rbac_client = RbacClient()


def require_permission(
    *codes: str, mode: str = "any"
) -> Callable[..., Awaitable[None]]:
    """Depends factory: 403 unless JWT user has the given permission code(s)."""

    async def _check(
        user_id: int = Depends(require_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        await _rbac_client.assert_permissions(user_id, db, list(codes), mode=mode)

    return _check


def require_role(
    *role_names: str, mode: str = "any"
) -> Callable[..., Awaitable[None]]:
    """Depends factory: 403 unless JWT user has the given role name(s)."""

    async def _check(
        user_id: int = Depends(require_current_user_id),
        db: Session = Depends(get_db),
    ) -> None:
        _rbac_client.assert_roles(user_id, db, list(role_names), mode=mode)

    return _check
