from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.routes import register_v1_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.environment == "development":
        from app.core.db import init_development_tables

        init_development_tables()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(register_v1_routes(), prefix=settings.api_v1_prefix)
    return app


app = create_app()
