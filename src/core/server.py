from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.helpers.logger import Logger
from src.helpers.middlewares import LogRequests

logger = Logger(__name__)


class Server:
    def __init__(self):
        self.logger = Logger(__name__)
        self.app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
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

    def get_app(self):
        return self.app
