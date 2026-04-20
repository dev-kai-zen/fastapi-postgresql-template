from fastapi import APIRouter, Cookie, Query, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.core.config import get_settings
from app.core.constants import REFRESH_TOKEN_COOKIE_NAME
from app.modules.auth import service
from app.modules.auth.schema import AccessTokenResponse, UserInfoResponse

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


@router.get("/google/login", include_in_schema=False)
async def google_login_get():
    return _google_login_redirect()


@router.post("/google/login", include_in_schema=False)
async def google_login_post():
    return _google_login_redirect()


@router.get("/google/callback", include_in_schema=False)
async def google_callback(code: str = Query(...)):
    result = await service.complete_google_oauth(code)
    body = AccessTokenResponse(access_token=result.access_token)
    response = JSONResponse(content=body.model_dump(mode="json"))
    _set_refresh_token_cookie(response, result.refresh_token)
    return response


@router.post("/retry-login", response_model=AccessTokenResponse, include_in_schema=False)
async def retry_login(
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
):
    access = service.refresh_access_from_cookie(refresh_token)
    return AccessTokenResponse(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
def logout(
    refresh_token: str | None = Cookie(None, alias=REFRESH_TOKEN_COOKIE_NAME),
) -> Response:
    service.logout_revoking_refresh_token(refresh_token)
    out = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(out)
    return out


@router.get("/user-info", response_model=UserInfoResponse, include_in_schema=False)
def user_info():
    return service.get_user_info()