from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class GoogleTokenRequest(BaseModel):
    code: str = Field(min_length=1, description="Authorization code from Google.")
    redirect_uri: str | None = Field(
        default=None,
        description="If omitted, GOOGLE_REDIRECT_URI from settings is used.",
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class AuthorizationUrlResponse(BaseModel):
    authorization_url: str
