from typing import Any

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlmodel.sql._expression_select_cls import SelectOfScalar

from helpers.auth import hash_password
from helpers.logger import logger
from helpers.repository import BaseRepository
from helpers.utils import APIError, APIResponse
from models.auth import UserAuthenticate, UserManage
from models.users import Users


class AuthService(BaseRepository):
    async def validate(self, payload: UserAuthenticate) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        hashed_password: str = hash_password(payload.password)
        user: Any = Users(
            **payload.model_dump(exclude={"password"}),
            password=hashed_password,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await self.close_database_session()
        return APIResponse(data=user.model_dump())

    async def manage(self, action: str, payload: UserManage) -> APIResponse:
        db: AsyncSession = await self.get_database_session()
        user_id = ""
        statement: SelectOfScalar[type[Users]] = select(Users).where(
            Users.id == user_id
        )
        result: Result[tuple[type[Users]]] = await db.execute(statement)
        user: type[Users] | None = result.scalar_one_or_none()
        if not user:
            logger.error(f"User not found: {user_id}")
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
