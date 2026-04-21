from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.core.security import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
    revoke_refresh_token,
)
from app.modules.auth.oauth_client import GoogleOAuthClient, OAuthClientError
from app.modules.auth.rbac_client import RbacClient
from app.modules.auth.schema import UserInfoResponse
from app.modules.auth.users_client import UsersClient

_oauth_client = GoogleOAuthClient()
_users_client = UsersClient()
_rbac_client = RbacClient()


@dataclass(frozen=True)
class GoogleOAuthCompleteResult:
    access_token: str
    refresh_token: str


def get_google_login_redirect_url() -> str:
    return _oauth_client.build_authorization_url()


async def complete_google_oauth(code: str) -> GoogleOAuthCompleteResult:
    try:
        tokens = await _oauth_client.exchange_code_for_tokens(code)
        raw_profile = await _oauth_client.get_user_info(tokens["access_token"])
    except OAuthClientError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    db: Session = SessionLocal()
    try:
        user_read = _users_client.upsert_google_identity(db, raw_profile)
        role_id = _rbac_client.get_primary_role_id_for_user(db, user_read.id)
        permissions = _rbac_client.list_permissions_for_user(db, user_read.id)
        user_claims = user_read.model_dump(mode="json")
        user_claims["role_id"] = role_id
        access = create_access_token(user_claims, permissions=permissions)
        refresh = create_refresh_token(
            user_read.id,
            extra_claims={"user": user_claims, "permissions": permissions},
        )
        return GoogleOAuthCompleteResult(
            access_token=access,
            refresh_token=refresh,
        )
    finally:
        db.close()


def refresh_access_from_cookie(refresh_token: str | None) -> str:
    """Mint a new access token from the refresh cookie; raises HTTPException if missing/invalid."""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    return refresh_access_token(refresh_token)


def logout_revoking_refresh_token(refresh_token: str | None) -> None:
    """Best-effort revoke refresh JWT (Redis); ignores errors so logout always clears cookie."""
    if not refresh_token:
        return
    try:
        revoke_refresh_token(refresh_token)
    except Exception:
        pass


def get_user_info() -> UserInfoResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented",
    )
