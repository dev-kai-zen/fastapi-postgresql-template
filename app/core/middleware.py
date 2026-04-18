from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.core.constants import NEW_ACCESS_TOKEN_HEADER


def _cors_allow_origins(settings: Settings) -> list[str]:
    raw = settings.cors_allow_origins.strip()
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    parsed = urlparse(settings.frontend_oauth_success_url)
    if parsed.scheme and parsed.netloc:
        return [f"{parsed.scheme}://{parsed.netloc}"]
    return []


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Attach Starlette/FastAPI middleware. Order: first registered = outermost."""
    origins = _cors_allow_origins(settings)
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[NEW_ACCESS_TOKEN_HEADER],
        )
