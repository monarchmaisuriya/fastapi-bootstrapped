from typing import Annotated, Any

from fastapi import APIRouter
from fastapi.params import Depends

from helpers.auth import public_route, require_auth
from helpers.utils import APIResponse
from models.users import (
    UserAuthRead,
    UserCreate,
    UserInvalidate,
    UserManage,
    UserManageAction,
    UserRead,
    UserRevalidate,
    UserUpdate,
    UserValidate,
)
from services.users import UserService

user_router: APIRouter = APIRouter(prefix="/api/v1/users", tags=["users"])
user_service: UserService = UserService()


@user_router.get(
    "/account",
    response_model=APIResponse[UserRead],
    summary="Get current user info",
    description="Fetch details of the authenticated user using their access token.",
)
async def get(auth: Annotated[dict[str, Any], Depends(require_auth)]):
    return await user_service.get(auth["sub"])


@user_router.patch(
    "/account",
    response_model=APIResponse[UserRead],
    summary="Update user info",
    description="Update the authenticated user's information such as name or profile settings.",
)
async def update(
    payload: UserUpdate, auth: Annotated[dict[str, Any], Depends(require_auth)]
):
    return await user_service.update(auth["sub"], payload)


@user_router.post(
    "/account",
    response_model=APIResponse[UserRead],
    summary="Create a new user account",
    description="Create a new user account using the provided details.",
)
@public_route
async def create(payload: UserCreate):
    return await user_service.create(payload)


@user_router.post(
    "/account/validate",
    response_model=APIResponse[UserAuthRead],
    summary="Validate user credentials",
    description="Validate a user's login credentials and return authentication data.",
)
@public_route
async def validate(payload: UserValidate):
    return await user_service.validate(payload)


@user_router.post(
    "/account/revalidate",
    response_model=APIResponse[UserAuthRead],
    summary="Revalidate a session",
    description="Revalidate an existing session using a refresh token.",
)
async def revalidate(payload: UserRevalidate):
    return await user_service.revalidate(payload)


@user_router.post(
    "/account/invalidate",
    response_model=APIResponse[dict],
    summary="Invalidate a session",
    description="Invalidate an existing session using a refresh token.",
)
async def invalidate(payload: UserInvalidate):
    return await user_service.invalidate(payload)


@user_router.post(
    "/account/manage/{action}",
    response_model=APIResponse[UserAuthRead],
    summary="Manage user account actions",
    description="Perform management actions (like password reset or account recovery) on a user account.",
)
async def manage(action: UserManageAction, payload: UserManage):
    return await user_service.manage(action, payload)
