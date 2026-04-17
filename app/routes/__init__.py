from fastapi import APIRouter

from app.modules.app_testing.app_testing_routes import router as routes_test_router
from app.modules.auth.router import router as auth_router
from app.modules.items.router import router as items_router
from app.modules.users.router import router as users_router


def register_v1_routes() -> APIRouter:
    router = APIRouter()
    router.include_router(routes_test_router)
    router.include_router(auth_router)
    router.include_router(items_router)
    router.include_router(users_router)
    return router
