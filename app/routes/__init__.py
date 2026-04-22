from fastapi import APIRouter

from app.modules.app_testing.app_testing_routes import router as routes_test_router
from app.modules.auth.router import router as auth_router
from app.modules.rbac.group.router import router as rbac_groups_router
from app.modules.rbac.permissions.router import router as rbac_permissions_router
from app.modules.rbac.role.router import router as rbac_roles_router
from app.modules.rbac.role_permissions.router import (
    router as rbac_role_permissions_router,
)
from app.modules.rbac.user_roles.router import router as rbac_user_roles_router
from app.modules.users.router import router as users_router


def register_v1_routes() -> APIRouter:
    router = APIRouter()
    router.include_router(routes_test_router)
    router.include_router(auth_router)
    router.include_router(users_router)
    router.include_router(rbac_groups_router)
    router.include_router(rbac_permissions_router)
    router.include_router(rbac_roles_router)
    router.include_router(rbac_role_permissions_router)
    router.include_router(rbac_user_roles_router)
    return router
