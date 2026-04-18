import httpx

from app.core.config import get_settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


class OAuthClientError(Exception):
    def __init__(self, status_code: int, detail: str | dict):
        self.status_code = status_code
        self.detail = detail
        super().__init__(repr(detail))


class GoogleOAuthClient:
    def build_authorization_url(self) -> str:
        settings = get_settings()
        return (
            f"{GOOGLE_AUTH_URL}"
            f"?client_id={settings.google_client_id}"
            f"&redirect_uri={settings.google_redirect_uri}"
            "&response_type=code"
            "&scope=openid%20email%20profile"
        )

    async def exchange_code_for_tokens(self, code: str) -> dict:
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                },
            )
        if response.status_code != 200:
            detail: str | dict = "Failed to exchange code for tokens"
            try:
                detail = response.json()
            except Exception:
                detail = response.text or detail
            raise OAuthClientError(status_code=400, detail=detail)
        return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code != 200:
            raise OAuthClientError(
                status_code=400, detail="Failed to get user info"
            )
        return response.json()
