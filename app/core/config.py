from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str  # from env APP_NAME
    environment: str = "development"  # from env ENVIRONMENT
    debug: bool = False  # from env DEBUG

    api_v1_prefix: str  # from env API_V1_PREFIX

    database_url: str  # from env DATABASE_URL
    redis_url: str  # from env REDIS_URL

    jwt_secret_key: str  # from env JWT_SECRET_KEY
    jwt_algorithm: str  # from env JWT_ALGORITHM
    access_token_expire_minutes: int  # from env ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_days: int  # from env REFRESH_TOKEN_EXPIRE_DAYS

    google_client_id: str  # from env GOOGLE_CLIENT_ID
    google_client_secret: str  # from env GOOGLE_CLIENT_SECRET
    # Must match an authorized redirect URI in Google Cloud Console (used in token exchange).
    google_redirect_uri: str | None = None  # from env GOOGLE_REDIRECT_URI
    # After Google OAuth, the API redirects the browser here with `#access_token=<jwt>`.
    # from env FRONTEND_OAUTH_SUCCESS_URL
    frontend_oauth_success_url: str = "http://localhost:5173/auth/callback"
    # Comma-separated browser origins allowed for credentialed CORS (e.g. `http://localhost:5173`).
    # If empty, the origin of `frontend_oauth_success_url` is used.
    cors_allow_origins: str = ""  # from env CORS_ALLOW_ORIGINS

    # Redis-backed per-IP limits on routes under `api_v1_prefix` (see `RateLimitMiddleware`).
    # Defaults apply when env vars are omitted (e.g. Docker compose without these keys).
    rate_limit_enabled: bool = True  # from env RATE_LIMIT_ENABLED
    rate_limit_window_seconds: int = 60  # from env RATE_LIMIT_WINDOW_SECONDS
    rate_limit_auth_per_minute: int = 40  # from env RATE_LIMIT_AUTH_PER_MINUTE
    rate_limit_api_per_minute: int = 200  # from env RATE_LIMIT_API_PER_MINUTE

    # Dev/test only: shared secret for `/app-testing/generate-token` (see app_testing routes).
    app_testing_admin_code: str = "api-test"  # from env APP_TESTING_ADMIN_CODE; empty = route disabled
    app_testing_token_expire_minutes: int = 30  # from env APP_TESTING_TOKEN_EXPIRE_MINUTES


# Env / .env supply fields; pyright cannot see that at call time.
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
