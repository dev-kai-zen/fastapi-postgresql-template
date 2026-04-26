import secrets
from datetime import timedelta
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.dependencies.token_payload_deps import require_access_token_payload
from app.core.security import create_access_token

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Connected to the API: {get_settings().app_name}"}


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "Healthy", "service": settings.app_name}


@router.get("/db-ping")
def db_ping(db: Session = Depends(get_db)) -> dict[str, bool | int]:
    one = cast(int, db.execute(text("SELECT 1")).scalar_one())
    return {"ok": True, "select_1": one}


@router.get("/app-testing/token-check")
def token_check(
    payload: dict = Depends(require_access_token_payload),
) -> dict[str, Any]:
    """Requires a valid access JWT (Authorization: Bearer). For manual / UI testing."""
    return {"valid": True, "sub": payload.get("sub")}


def _mint_app_testing_access_token(admin_code: str) -> dict[str, Any]:
    """Issue a short-lived JWT for local/manual API testing. Gated by env + shared secret."""
    settings = get_settings()
    if settings.environment not in ("development", "test"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App testing token minting is only allowed in development or test",
        )
    expected = (settings.app_testing_admin_code or "").strip()
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="App testing token minting is disabled (set APP_TESTING_ADMIN_CODE)",
        )
    try:
        valid = len(admin_code) == len(expected) and secrets.compare_digest(
            admin_code, expected
        )
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin code",
        )
    # Synthetic subject only (not a DB user) — for exercising JWT-protected routes; avoid /users/me.
    expires = timedelta(minutes=max(1, settings.app_testing_token_expire_minutes))
    access = create_access_token(0, expires_delta=expires)
    return {
        "access_token": access,
        "token_type": "bearer",
        "expires_in_minutes": settings.app_testing_token_expire_minutes,
    }


@router.get("/app-testing/generate-token")
def generate_token(
    admin_code: str = Query(
        ...,
        alias="admin-code",
        description="Must match APP_TESTING_ADMIN_CODE (dev/test only).",
    ),
) -> dict[str, Any]:
    """Return a temporary access JWT for manual testing (`Authorization: Bearer ...`)."""
    return _mint_app_testing_access_token(admin_code)
