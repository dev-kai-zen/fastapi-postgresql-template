from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import REFRESH_TOKEN_COOKIE_NAME
from app.core.db import get_db
from app.core.security import refresh_access_token, revoke_refresh_token
from app.modules.auth import service
from app.modules.auth.schema import AccessTokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_token_cookie(response: RedirectResponse, refresh_token: str) -> None:
    settings = get_settings()
    max_age = settings.refresh_token_expire_days * 86400
    secure = settings.environment not in ("development", "test")
    # Scope to all v1 API routes so protected handlers can receive it (not only /auth).
    path = settings.api_v1_prefix.rstrip("/") or "/"
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=secure,
        samesite="lax",
        path=path,
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Expire the refresh cookie; must match path/flags used in _set_refresh_token_cookie."""
    settings = get_settings()
    secure = settings.environment not in ("development", "test")
    path = settings.api_v1_prefix.rstrip("/") or "/"
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path=path,
        secure=secure,
        httponly=True,
        samesite="lax",
    )


def _google_login_redirect() -> RedirectResponse:
    return RedirectResponse(service.get_google_login_redirect_url())


@router.get("/google/login")
async def google_login_get():
    return _google_login_redirect()


@router.post("/google/login")
async def google_login_post():
    return _google_login_redirect()


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    db: Session = Depends(get_db),
):
    result = await service.complete_google_oauth(db, code)
    response = RedirectResponse(result.redirect_url)
    _set_refresh_token_cookie(response, result.refresh_token)
    return response


@router.post("/retry-login", response_model=AccessTokenResponse)
async def retry_login(
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    access = refresh_access_token(refresh_token)
    return AccessTokenResponse(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> Response:
    if refresh_token:
        try:
            revoke_refresh_token(refresh_token)
        except Exception:
            pass
    out = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(out)
    return out
