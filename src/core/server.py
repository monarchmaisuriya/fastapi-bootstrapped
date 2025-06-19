from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import check_database_connection, engine
from helpers.logger import Logger
from helpers.middlewares import LogRequests

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
        cors_origins = (
            settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
        )
        self.app.add_middleware(
            # type: ignore[arg-type] - Known issue with FastAPI and Starlette types
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # type: ignore[arg-type]  - Known issue with FastAPI and Starlette types
        self.app.add_middleware(LogRequests)

    @asynccontextmanager
    async def _lifespan_context(self, app: FastAPI) -> AsyncGenerator[None, None]:
        if not await check_database_connection(engine):
            raise RuntimeError("Database connection failed after retries")

        self.logger.info("Database connection established successfully")
        yield

    def get_app(self) -> FastAPI:
        return self.app
