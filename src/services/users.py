from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.repository import BaseRepository
from src.helpers.utils import APIError, APIResponse
from src.models.users import User


class UserRepository(BaseRepository[User]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()


repository = UserRepository(User)


async def get_user(id: str, db: AsyncSession = Request.state.db):
    user = await repository.get(db, id)
    if not user:
        raise APIError(404, "User not found")
    return APIResponse(data=user.model_dump())


async def update_user(id: str, db: AsyncSession = Request.state.db):
    user = await repository.get(db, id)
    if not user:
        raise APIError(404, "User not found")
    return APIResponse(data=user.model_dump())


async def signup_user(db: AsyncSession = Request.state.db):
    return APIResponse(data="signup")


async def signin_user(db: AsyncSession = Request.state.db):
    return APIResponse(data="signin")


async def manage_user(db: AsyncSession = Request.state.db):
    return APIResponse(data="manage")
