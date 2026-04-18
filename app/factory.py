from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware
from app.routes import register_v1_routes


def _expose_openapi(settings: Settings) -> bool:
    env = settings.environment.lower()
    if env in ("production", "prod"):
        return bool(settings.openapi_docs_in_production)
    return True


def create_app() -> FastAPI:
    settings = get_settings()
    expose = _expose_openapi(settings)
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        docs_url="/docs" if expose else None,
        redoc_url="/redoc" if expose else None,
        openapi_url="/openapi.json" if expose else None,
    )
    register_middleware(app, settings)
    app.include_router(register_v1_routes(), prefix=settings.api_v1_prefix)
    return app
