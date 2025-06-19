import time
from typing import Any

from api import setup_routes
from core.config import settings
from core.server import Server
from helpers.auth import get_public_paths, public_route
from middlewares.auth import AuthenticateRequest

# Initialize server
server = Server()
app = server.get_app()

# Include API routers
app.include_router(setup_routes())


# Health check endpoints
@app.get("/health")
@public_route
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


# Add custom middlewares
public_paths = get_public_paths(app)
app.add_middleware(
    # type: ignore[arg-type]  - Known issue with FastAPI and Starlette types
    AuthenticateRequest,
    public_paths=public_paths,
)
