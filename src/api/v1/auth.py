from fastapi import APIRouter

from models.auth import UserAuthenticate, UserManage
from models.users import UserCreate
from services.auth import AuthService
from services.users import UserService

users_router = APIRouter(prefix="/api/v1/auth", tags=["users"])
auth_service = AuthService()
user_service = UserService()


@users_router.post("/account/create")
async def create(payload: UserCreate):
    return await user_service.create(payload)


@users_router.post("/account/validate")
async def validate(payload: UserAuthenticate):
    return await auth_service.validate(payload)


@users_router.post("/account/manage/{action}")
async def manage(action: str, payload: UserManage):
    return await auth_service.manage(action, payload)
