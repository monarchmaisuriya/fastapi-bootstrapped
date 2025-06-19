from uuid import UUID

from fastapi import APIRouter

from models.users import UserUpdate
from services.users import UserService

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])
user_service = UserService()


@users_router.get("/{id}")
async def get(id: UUID):
    return await user_service.get(id)


@users_router.patch("/{id}")
async def update(id: UUID, payload: UserUpdate):
    return await user_service.update(id, payload)
