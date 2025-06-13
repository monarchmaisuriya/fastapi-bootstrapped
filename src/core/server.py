from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.database import check_database_connection, engine
from src.helpers.logger import Logger
from src.helpers.middlewares import LogRequests

logger = Logger(__name__)


class Server:
    def __init__(self):
        self.logger = Logger(__name__)
        self.app = FastAPI(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            lifespan=self._lifespan_context,
        )
        self._configure_middlewares()

    def _configure_middlewares(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS.split(","),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_middleware(LogRequests)

    @asynccontextmanager
    async def _lifespan_context(self, app: FastAPI) -> AsyncGenerator[None, None]:
        app.state.db = {"engine": engine}
        if not await check_database_connection(app.state.db["engine"]):
            raise RuntimeError("Database connection failed after retries")
        yield

    def get_app(self):
        return self.app
