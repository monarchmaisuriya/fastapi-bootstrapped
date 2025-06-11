import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.core.config import settings


def Logger(name: str = settings.PROJECT_NAME) -> logging.Logger:
    """Configure and return a logger instance based on environment settings."""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # Always add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler in production
    if settings.ENV.lower() == "production":
        # Ensure log directory exists
        log_dir = Path(settings.LOG_DIR)
        log_dir.mkdir(exist_ok=True)

        # Setup rotating file handler
        file_handler = RotatingFileHandler(
            filename=log_dir / settings.LOG_FILE,
            maxBytes=settings.LOG_FILE_MAX_BYTES,
            backupCount=settings.LOG_FILE_BACKUP_COUNT,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = Logger()
