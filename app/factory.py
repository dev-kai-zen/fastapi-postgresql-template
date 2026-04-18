from fastapi import FastAPI

from app.core.config import get_settings
from app.core.lifespan import lifespan
from app.core.middleware import register_middleware
from app.routes import register_v1_routes


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    register_middleware(app, settings)
    app.include_router(register_v1_routes(), prefix=settings.api_v1_prefix)
    return app
