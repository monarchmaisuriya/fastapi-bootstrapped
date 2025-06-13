from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from src.base.model import BaseModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# Unified ORM + Shared Pydantic Model
class User(BaseModel, table=True):
    email: str = Field(index=True, unique=True, max_length=320)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    role: UserRole = Field(
        default=UserRole.USER,
        sa_type=SAEnum(UserRole),
        index=True,
        description="User role options",
    )
    password: str = Field(repr=False)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    verification_token: str | None = None
    verification_token_expires: datetime | None = None
    reset_token: str | None = None
    reset_token_expires: datetime | None = None
    last_login_at: datetime | None = None
    metadata: dict = Field(default_factory=dict)


# Pydantic Models
class UserCreate(SQLModel):
    email: str
    first_name: str
    last_name: str
    password: str
    role: UserRole | None = None


class UserRead(SQLModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
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
