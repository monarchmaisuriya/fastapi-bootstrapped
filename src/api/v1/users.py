from fastapi import APIRouter

from src.services.users import (
    get_user,
    manage_user,
    signin_user,
    signup_user,
    update_user,
)

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])

users_router.get("/{id}")(get_user)
users_router.patch("/{id}")(update_user)
users_router.post("/account/signup")(signup_user)
users_router.post("/account/signin")(signin_user)
users_router.post("/account/manage/{action}")(manage_user)
