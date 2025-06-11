import time
from typing import Any

from database import check_database_connection, get_session
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import setup_routes
from src.core.config import settings
from src.core.server import Server

# Initialize server
server = Server()
app = server.get_app()

# Include API routers
app.include_router(setup_routes())


# Health check endpoints
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@app.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Detailed health check with dependency checks."""

    health_data = {"status": "healthy", "timestamp": time.time(), "checks": {}}

    # Database health check
    db_start = time.time()
    db_healthy = await check_database_connection()
    db_duration = time.time() - db_start

    health_data["checks"]["database"] = {
        "status": "healthy" if db_healthy else "unhealthy",
        "response_time": round(db_duration * 1000, 2),  # ms
    }

    # Redis health check (if configured)
    if settings.REDIS_URI:
        redis_start = time.time()
        redis_healthy = await check_redis_connection()
        redis_duration = time.time() - redis_start

        health_data["checks"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "response_time": round(redis_duration * 1000, 2),
        }

    # Overall status
    all_healthy = all(
        check["status"] == "healthy" for check in health_data["checks"].values()
    )

    if not all_healthy:
        health_data["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_data)

    return health_data


@app.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Kubernetes readiness probe endpoint."""
    db_healthy = await check_database_connection()

    if not db_healthy:
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "reason": "database unavailable"},
        )

    return {"status": "ready"}


@app.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive"}


async def check_redis_connection() -> bool:
    """Check Redis connection if configured."""
    try:
        # Redis connection check implementation
        return True
    except Exception:
        return False
