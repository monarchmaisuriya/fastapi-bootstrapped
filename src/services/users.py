from typing import Any
from uuid import UUID

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from helpers.auth import hash_password
from helpers.repository import BaseRepository
from helpers.utils import APIError, APIResponse
from models.users import UserCreate, UserQuery, Users, UserUpdate


class UserService(BaseRepository):
    async def create(self, payload: UserCreate) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        user: Any = Users(
            **payload.model_dump(exclude={"password"}),
            password=hash_password(payload.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await self.close_database_session()
        return APIResponse(data=user.model_dump())

    async def find(self, query: UserQuery) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        filters: list[bool] = []
        if query.first_name:
            filters.append(Users.first_name == query.first_name)
        if query.last_name:
            filters.append(Users.last_name == query.last_name)
        if query.email:
            filters.append(Users.email == query.email)

        stmt: SelectOfScalar[type[Users]] = select(Users)
        if filters:
            stmt = stmt.where(*filters)

        result: Result[tuple[type[Users]]] = await db.execute(stmt)
        user: type[Users] | None = result.scalar_one_or_none()
        await self.close_database_session()

        if not user:
            raise APIError(404, "User not found")

        return APIResponse(data=Users(user).model_dump())

    async def get(self, id: UUID) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        stmt: SelectOfScalar[type[Users]] = select(Users).where(Users.id == id)
        result: Result[tuple[type[Users]]] = await db.execute(stmt)
        user: type[Users] | None = result.scalar_one_or_none()
        await self.close_database_session()

        if not user:
            raise APIError(404, "User not found")
        return APIResponse(data=Users(user).model_dump())

    async def update(self, id: UUID, payload: UserUpdate) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        stmt: SelectOfScalar[type[Users]] = select(Users).where(Users.id == id)
        result: Result[tuple[type[Users]]] = await db.execute(stmt)
        user: type[Users] | None = result.scalar_one_or_none()
        if not user:
            await self.close_database_session()
            raise APIError(404, "User not found")

        update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(user, key, value)

        db.add(user)
        await db.commit()
        await db.refresh(user)
        await self.close_database_session()
        return APIResponse(data=Users(user).model_dump())

    async def delete(self, id: UUID) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        stmt: SelectOfScalar[type[Users]] = select(Users).where(Users.id == id)
        result: Result[tuple[type[Users]]] = await db.execute(stmt)
        user: type[Users] | None = result.scalar_one_or_none()
        if not user:
            await self.close_database_session()
            raise APIError(404, "User not found")
        await db.delete(user)
        await db.commit()
        await self.close_database_session()
        return APIResponse(data={"message": "User deleted"})
