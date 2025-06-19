from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_database_session
from helpers.auth import hash_password
from helpers.logger import logger
from helpers.utils import APIError, APIResponse
from models.users import UserCreate, UserQuery, Users, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession = Depends(get_database_session)):
        self.db = db

    async def create(self, payload: UserCreate) -> APIResponse:
        hashed_password = hash_password(payload.password)
        user = Users(
            **payload.model_dump(exclude={"password"}), password=hashed_password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return APIResponse(data=user.model_dump())

    async def find(self, query: UserQuery | None = None) -> APIResponse:
        filters = []
        if query:
            if query.first_name:
                filters.append(Users.first_name == query.first_name)
            if query.last_name:
                filters.append(Users.last_name == query.last_name)
            if query.email:
                filters.append(Users.email == query.email)

        statement = select(Users)
        if filters:
            statement = statement.where(*filters)

        result = await self.db.execute(statement)
        user = Users(result.scalar_one_or_none())

        if not user:
            logger.error(
                f"User not found with filters: {UserQuery(query).model_dump()}"
            )
            raise APIError(404, "User not found")

        return APIResponse(data=user.model_dump())

    async def get(self, id: UUID) -> APIResponse:
        statement = select(Users).where(Users.id == id)
        result = await self.db.execute(statement)
        user = Users(result.scalar_one_or_none())
        if not user:
            logger.error(f"User not found: {id}")
            raise APIError(404, "User not found")
        return APIResponse(data=user.model_dump())

    async def update(self, id: UUID, payload: UserUpdate) -> APIResponse:
        statement = select(Users).where(Users.id == id)
        result = await self.db.execute(statement)
        user = Users(result.scalar_one_or_none())
        if not user:
            logger.error(f"User not found: {id}")
            raise APIError(404, "User not found")

        update_data = payload.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return APIResponse(data=user.model_dump())

    async def delete(self, id: UUID) -> APIResponse:
        statement = select(Users).where(Users.id == id)
        result = await self.db.execute(statement)
        user = result.scalar_one_or_none()
        if not user:
            logger.error(f"User not found: {id}")
            raise APIError(404, "User not found")
        await self.db.delete(user)
        await self.db.commit()
        return APIResponse(data={"message": "User deleted"})
