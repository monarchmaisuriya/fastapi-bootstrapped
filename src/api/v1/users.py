from uuid import UUID

from fastapi import APIRouter

from models.users import UserRead, UserUpdate
from services.users import UserService

user_router: APIRouter = APIRouter(prefix="/api/v1/users", tags=["users"])
user_service: UserService = UserService()


@user_router.get("/{id}", response_model=UserRead)
async def get(id: UUID):
    return await user_service.get(id)


@user_router.patch("/{id}", response_model=UserRead)
async def update(id: UUID, payload: UserUpdate):
    return await user_service.update(id, payload)
