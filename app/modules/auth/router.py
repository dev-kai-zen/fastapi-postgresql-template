import httpx
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import revoke_refresh_token, verify_refresh_token
from app.modules.auth.dependencies import CurrentUser
from app.modules.users.interface import default_users_port
from app.modules.users.schema import UserRead

_users_port = default_users_port()

from . import service
from .schema import (
    AuthorizationUrlResponse,
    GoogleTokenRequest,
    RefreshRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _resolve_redirect_uri(explicit: str | None) -> str:
    settings = get_settings()
    configured = settings.google_redirect_uri
    if not configured:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Set GOOGLE_REDIRECT_URI in environment for Google OAuth.",
        )
    uri = explicit or configured
    if uri != configured:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="redirect_uri must match GOOGLE_REDIRECT_URI",
        )
    return uri


@router.get("/google/authorization-url", response_model=AuthorizationUrlResponse)
def google_authorization_url(
    redirect_uri: str | None = Query(
        default=None,
        description="Must match GOOGLE_REDIRECT_URI when provided.",
    ),
) -> AuthorizationUrlResponse:
    uri = _resolve_redirect_uri(redirect_uri)
    return AuthorizationUrlResponse(
        authorization_url=service.build_google_authorization_url(uri),
    )


@router.post("/google/token", response_model=TokenResponse)
def google_token(
    payload: GoogleTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    redirect = _resolve_redirect_uri(payload.redirect_uri)
    try:
        profile = service.exchange_google_code(payload.code, redirect)
        user = service.upsert_google_user(db, profile)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail="Google OAuth request failed",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return service.issue_tokens_for_user(user.id)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        payload = verify_refresh_token(body.refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc
    revoke_refresh_token(body.refresh_token)
    user_id = int(payload["sub"])
    if _users_port.get_by_id(db, user_id) is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )
    return service.issue_tokens_for_user(user_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: RefreshRequest) -> None:
    try:
        revoke_refresh_token(body.refresh_token)
    except jwt.PyJWTError:
        pass


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
