from typing import Annotated, Any

from fastapi import APIRouter
from fastapi.params import Depends

from helpers.auth import public_route, require_auth
from helpers.utils import APIResponse
from models.users import (
    UserAuthRead,
    UserCreate,
    UserManage,
    UserRead,
    UserRevalidate,
    UserUpdate,
    UserValidate,
)
from services.users import UserService

user_router: APIRouter = APIRouter(prefix="/api/v1/users", tags=["users"])
user_service: UserService = UserService()


@user_router.get("/", response_model=APIResponse[UserRead])
async def get(auth: Annotated[dict[str, Any], Depends(require_auth)]):
    return await user_service.get(auth["sub"])


@user_router.patch("/", response_model=APIResponse[UserRead])
async def update(
    payload: UserUpdate, auth: Annotated[dict[str, Any], Depends(require_auth)]
):
    return await user_service.update(auth["sub"], payload)


@user_router.post("/account/create", response_model=APIResponse[UserRead])
@public_route
async def create(payload: UserCreate):
    return await user_service.create(payload)


@user_router.post("/account/validate", response_model=APIResponse[UserAuthRead])
@public_route
async def validate(payload: UserValidate):
    return await user_service.validate(payload)


@user_router.post("/account/revalidate", response_model=APIResponse[UserAuthRead])
async def revalidate(payload: UserRevalidate):
    return await user_service.revalidate(payload)


@user_router.post("/account/manage/{action}", response_model=APIResponse[UserAuthRead])
async def manage(action: str, payload: UserManage):
    return await user_service.manage(action, payload)
