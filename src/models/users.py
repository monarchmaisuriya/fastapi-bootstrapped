from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from src.base.model import MetadataMixin, SoftDeleteMixin, TimestampMixin


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True, max_length=320)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(
        default=UserRole.USER,
        sa_type=SAEnum(UserRole),
        description="User role options",
        index=True,
    )
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class User(TimestampMixin, MetadataMixin, SoftDeleteMixin, UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str = Field(repr=False)
    verification_token: str | None = None
    verification_token_expires: datetime | None = None
    reset_token: str | None = None
    reset_token_expires: datetime | None = None
    last_login_at: datetime | None = None


# Pydantic Models
class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    role: UserRole
    metadata: dict
    created_at: datetime
    updated_at: datetime | None
    last_login_at: datetime | None


class UserUpdate(SQLModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    metadata: dict | None = None
    last_login_at: datetime | None = None
