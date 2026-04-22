from fastapi import APIRouter, Cookie, Depends, Query, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.constants import REFRESH_TOKEN_COOKIE_NAME
from app.core.db import get_db
from app.modules.auth import service
from app.modules.auth.schema import AccessTokenResponse, GoogleOAuthCompleteResult

from app.core.deps import require_access_token_payload


router = APIRouter(prefix="/auth", tags=["auth"])


def _set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    max_age = settings.refresh_token_expire_days * 86400
    secure = settings.environment not in ("development", "test")
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
async def google_callback(response: Response, code: str = Query(...)) -> GoogleOAuthCompleteResult:
    result = await service.complete_google_oauth(code)
    _set_refresh_token_cookie(response, result["refresh_token"])
    return GoogleOAuthCompleteResult(token=AccessTokenResponse(access_token=result["access_token"]), user=result["user"], roles=result["roles"], permissions=result["permissions"])


@router.post("/retry-login", response_model=AccessTokenResponse)
async def retry_login(
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> GoogleOAuthCompleteResult:
    result = service.refresh_access_from_cookie(db, refresh_token)
    return GoogleOAuthCompleteResult(token=AccessTokenResponse(access_token=result["access_token"]), user=result["user"], roles=result["roles"], permissions=result["permissions"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> Response:
    service.logout_revoking_refresh_token(db, refresh_token)
    out = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(out)
    return out
