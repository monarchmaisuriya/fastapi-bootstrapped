from typing import Any, Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Get a single record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def find(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, id: Any, obj_in: dict) -> ModelType | None:
        """Update an existing record."""
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
            .returning(self.model)
        )
        result = await db.execute(query)
        await db.commit()
        return result.scalar_one_or_none()

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record by ID."""
        query = delete(self.model).where(self.model.id == id)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
