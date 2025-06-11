import time
from typing import Any

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
