import logging
from collections.abc import AsyncGenerator

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from src.core.config import settings

logger = logging.getLogger(__name__)

DATABASE_URI = str(settings.POSTGRES_URI)

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
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


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def check_database_connection(db_engine: Engine) -> bool:
    """Health check for database connection."""
    try:
        AsyncSessionLocalCheck = async_sessionmaker(
            db_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with AsyncSessionLocalCheck() as session:
            # Try to create session to check if DB is awake
            await session.execute(select(1))
            logger.info("Database health check successful.")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
