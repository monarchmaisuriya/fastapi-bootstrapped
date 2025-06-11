import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.core.config import DATABASE_URI

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URI,
    # Connection pool settings
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    # SQLite specific (remove for PostgreSQL)
    poolclass=StaticPool if "sqlite" in DATABASE_URI else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URI else {},
    echo=False,  # Set to True for SQL logging in development
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables():
    """Create database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Health check for database connection."""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
    finally:
        await session.close()
