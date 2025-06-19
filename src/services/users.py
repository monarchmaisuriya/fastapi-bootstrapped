from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from helpers.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    rotate_refresh_token,
    verify_password,
    verify_refresh_token,
)
from helpers.repository import BaseRepository
from helpers.utils import APIError, APIResponse
from models.users import (
    UserAuthRead,
    UserCreate,
    UserManage,
    UserQuery,
    UserRead,
    UserRevalidate,
    Users,
    UserUpdate,
    UserValidate,
)


class UserService(BaseRepository):
    async def create(self, payload: UserCreate) -> APIResponse[UserRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(
                Users.email == payload.email,
                Users.is_deleted == False,  # noqa: E712
            )
            result = await db.execute(statement)
            if result.scalar_one_or_none():
                raise APIError(409, "User with this email already exists")

            user = Users(
                **payload.model_dump(exclude={"password"}),
                password=hash_password(payload.password),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            data = UserRead.model_validate(user).model_dump()
            return APIResponse[UserRead](data=data)
        except IntegrityError as e:
            await db.rollback()
            raise APIError(400, "Database integrity error") from e
        finally:
            await self.close_database_session()

    async def find(
        self,
        query: UserQuery,
        skip: int = 0,
        limit: int = 20,
        exclude_deleted: bool = True,
    ) -> APIResponse[UserRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            filters = []
            if query.first_name:
                filters.append(Users.first_name == query.first_name)
            if query.last_name:
                filters.append(Users.last_name == query.last_name)
            if query.email:
                filters.append(Users.email == query.email)
            if exclude_deleted:
                filters.append(Users.is_deleted == False)  # noqa: E712

            statement = select(Users)
            if filters:
                statement = statement.where(*filters)

            statement = statement.offset(skip).limit(limit)
            result = await db.execute(statement)
            users = result.scalars().all()

            data = [UserRead.model_validate(user) for user in users]
            return APIResponse[UserRead](
                data=[item.model_dump() for item in data],
                meta={"skip": skip, "limit": limit, "count": len(data)},
            )
        finally:
            await self.close_database_session()

    async def get(
        self, id: UUID, include_deleted: bool = False
    ) -> APIResponse[UserRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id)
            if not include_deleted:
                statement = statement.where(Users.is_deleted == False)  # noqa: E712

            result = await db.execute(statement)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            data = UserRead.model_validate(user).model_dump()
            return APIResponse[UserRead](data=data)
        finally:
            await self.close_database_session()

    async def update(
        self, id: UUID, payload: UserUpdate
    ) -> APIResponse[UserRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id, Users.is_deleted == False)  # noqa: E712
            result = await db.execute(statement)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            update_data = payload.model_dump(exclude_unset=True)

            new_email = update_data.get("email")
            if new_email and new_email != user.email:
                email_check_statement = select(Users).where(
                    Users.email == new_email,
                    Users.id != id,
                    Users.is_deleted == False,  # noqa: E712
                )
                email_check = await db.execute(email_check_statement)
                if email_check.scalar_one_or_none():
                    raise APIError(409, "Another user with this email already exists")

            if "password" in update_data:
                update_data["password"] = hash_password(update_data["password"])

            for key, value in update_data.items():
                setattr(user, key, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)
            data = UserRead.model_validate(user).model_dump()
            return APIResponse[UserRead](data=data)
        except IntegrityError as e:
            await db.rollback()
            raise APIError(400, "Database integrity error") from e
        finally:
            await self.close_database_session()

    async def delete(self, id: UUID) -> APIResponse[dict] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id, Users.is_deleted == False)  # noqa: E712
            result = await db.execute(statement)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            Users(user).soft_delete()
            db.add(user)
            await db.commit()
            return APIResponse[dict](data={"message": "User soft-deleted"})
        finally:
            await self.close_database_session()

    async def validate(self, payload: UserValidate) -> APIResponse[UserAuthRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            stmt = select(Users).where(
                Users.email == payload.email,
                Users.is_deleted == False,  # noqa: E712
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            if not verify_password(payload.password, user.password):
                raise APIError(401, "Invalid credentials")

            user.last_login_at = datetime.utcnow()
            db.add(user)
            await db.commit()
            await db.refresh(user)

            data = {
                "auth": {
                    "access_token": create_access_token(user.id),
                    "refresh_token": create_refresh_token(user.id),
                },
                "user": UserRead.model_validate(user).model_dump(),
            }
            return APIResponse[UserAuthRead](data=data)
        finally:
            await self.close_database_session()

    async def revalidate(
        self, payload: UserRevalidate
    ) -> APIResponse[UserAuthRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            auth_data = verify_refresh_token(payload.refresh_token)
            if not auth_data:
                raise APIError(401, "Invalid or expired refresh token")

            user_email = auth_data["sub"]
            access_token, new_refresh_token = rotate_refresh_token(
                payload.refresh_token
            )

            stmt = select(Users).where(
                Users.email == user_email,
                Users.is_deleted == False,  # noqa: E712
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            data = {
                "auth": {
                    "access_token": access_token,
                    "refresh_token": new_refresh_token,
                },
                "user": UserRead.model_validate(user).model_dump(),
            }
            return APIResponse[UserAuthRead](data=data)
        finally:
            await self.close_database_session()

    async def manage(
        self, action: str, payload: UserManage
    ) -> APIResponse[UserAuthRead] | None:
        db: AsyncSession = await self.get_database_session()
        try:
            stmt = select(Users).where(
                Users.id == "",  # Replace with actual logic
                Users.is_deleted == False,  # noqa: E712
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["password"] = hash_password(update_data["password"])

            for key, value in update_data.items():
                setattr(user, key, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)
            data = UserRead.model_validate(user).model_dump()
            return APIResponse[UserAuthRead](data=data)
        except IntegrityError as e:
            await db.rollback()
            raise APIError(400, "Database error while managing user") from e
        finally:
            await self.close_database_session()
