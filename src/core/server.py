from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from core.config import settings
from core.database import check_database_connection, engine
from helpers.logger import Logger
from helpers.middlewares import LogRequests

if TYPE_CHECKING:
    from starlette.datastructures import State

logger = Logger(__name__)


class DBState:
    def __init__(self, engine: AsyncEngine):
        self.engine = engine


def get_db_state(state: "State") -> DBState:
    """Type-safe getter for database state."""
    return state["db"]


def set_db_state(state: "State", db_state: DBState) -> None:
    """Type-safe setter for database state."""
    state["db"] = db_state


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
        db_state = DBState(engine)
        set_db_state(app.state, db_state)

        current_db_state = get_db_state(app.state)
        if not await check_database_connection(current_db_state.engine):
            raise RuntimeError("Database connection failed after retries")

        self.logger.info("Database connection established successfully")
        yield

    def get_app(self) -> FastAPI:
        return self.app

    def get_db_from_state(self) -> DBState:
        """Helper method to get database state from the app."""
        return get_db_state(self.app.state)
