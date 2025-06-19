from uuid import UUID

from fastapi import APIRouter

from models.users import UserRead, UserUpdate
from services.users import UserService

users_router = APIRouter(prefix="/api/v1/users", tags=["users"])
user_service = UserService()


@users_router.get("/{id}", response_model=UserRead)
async def get(id: UUID):
    return await user_service.get(id)


@users_router.patch("/{id}", response_model=UserRead)
async def update(id: UUID, payload: UserUpdate):
    return await user_service.update(id, payload)
