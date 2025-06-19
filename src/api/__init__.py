from fastapi import APIRouter

from api.v1.auth import auth_router
from api.v1.users import users_router


def setup_routes() -> APIRouter:
    """Configure and return the main API router with all routes."""
    router = APIRouter()
    router.include_router(auth_router)
    router.include_router(users_router)
    return router
