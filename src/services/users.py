from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from helpers.auth import hash_password
from helpers.repository import BaseRepository
from helpers.utils import APIError, APIResponse
from models.users import UserCreate, UserQuery, Users, UserUpdate


class UserService(BaseRepository):
    async def create(self, payload: UserCreate) -> APIResponse | None:
        db: AsyncSession = await self.get_database_session()
        try:
            # Check for existing active user
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
            return APIResponse(data=user.model_dump())
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
        include_deleted: bool = False,
    ) -> APIResponse | None:
        db: AsyncSession = await self.get_database_session()
        try:
            filters = []
            if query.first_name:
                filters.append(Users.first_name == query.first_name)
            if query.last_name:
                filters.append(Users.last_name == query.last_name)
            if query.email:
                filters.append(Users.email == query.email)
            if not include_deleted:
                filters.append(Users.is_deleted == False)  # noqa: E712

            statement = select(Users)
            if filters:
                statement = statement.where(*filters)

            statement = statement.offset(skip).limit(limit)
            result = await db.execute(statement)
            users = result.scalars().all()

            return APIResponse(
                data=[Users(user).model_dump() for user in users],
                meta={"skip": skip, "limit": limit, "count": len(users)},
            )
        finally:
            await self.close_database_session()

    async def get(self, id: UUID, include_deleted: bool = False) -> APIResponse | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id)
            if not include_deleted:
                statement = statement.where(Users.is_deleted == False)  # noqa: E712

            result = await db.execute(statement)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            return APIResponse(data=(Users(user).model_dump()))
        finally:
            await self.close_database_session()

    async def update(self, id: UUID, payload: UserUpdate) -> APIResponse | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id, Users.is_deleted == False)  # noqa: E712
            result = await db.execute(statement)
            user: type[Users] | None = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            update_data = payload.model_dump(exclude_unset=True)

            # If changing email, ensure it's not taken
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

            # Handle password hash if added
            if "password" in update_data:
                update_data["password"] = hash_password(update_data["password"])

            for key, value in update_data.items():
                setattr(user, key, value)

            db.add(user)
            await db.commit()
            await db.refresh(user)
            return APIResponse(data=(Users(user).model_dump()))
        except IntegrityError as e:
            await db.rollback()
            raise APIError(400, "Database integrity error") from e
        finally:
            await self.close_database_session()

    async def delete(self, id: UUID) -> APIResponse | None:
        db: AsyncSession = await self.get_database_session()
        try:
            statement = select(Users).where(Users.id == id, Users.is_deleted == False)  # noqa: E712
            result = await db.execute(statement)
            user = result.scalar_one_or_none()

            if not user:
                raise APIError(404, "User not found")

            # Soft delete
            Users(user).soft_delete()
            db.add(user)
            await db.commit()
            return APIResponse(data={"message": "User soft-deleted"})
        finally:
            await self.close_database_session()
