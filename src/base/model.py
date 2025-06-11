import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(datetime.timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class MetadataMixin(SQLModel):
    metadata: dict = Field(default_factory=dict)


class SoftDeleteMixin(SQLModel):
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.now(datetime.timezone.utc)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(TimestampMixin, SoftDeleteMixin):
    id: str | None = Field(
        default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True
    )
