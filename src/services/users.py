from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.repository import BaseRepository
from src.helpers.utils import APIError, APIResponse
from src.models.users import User, UserCreate
from src.services.auth import hash_password


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


async def signup_user(request: Request, db: AsyncSession = Request.state.db):
    body = await request.json()
    try:
        data = UserCreate(**body)
    except Exception as e:
        raise APIError(422, "Invalid input")
    existing_user = await repository.get_by_email(db, data.email)
    if existing_user:
        raise APIError(409, "User already exists")
    hashed_password = hash_password(data.password)
    user_obj = data.model_dump(exclude={"password"})
    user_obj["password"] = hashed_password
    created_user = await repository.create(db, user_obj)

    return APIResponse(
        message="Signup successful",
        data={"id": created_user.id, "email": created_user.email},
    )


async def signin_user(db: AsyncSession = Request.state.db):
    return APIResponse(data="signin")


async def manage_user(action: str, db: AsyncSession = Request.state.db):
    return APIResponse(data="manage")
