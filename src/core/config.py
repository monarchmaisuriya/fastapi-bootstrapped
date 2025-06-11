from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Bootstrapped"  # Project name
    VERSION: str = "0.1.0"

    # Environment settings
    BASE_URL: str = ""
    ENV: str = "development"

    # JWT settings
    JWT_SECRET: str = "secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Logging settings
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"
    LOG_FILE: str = "server.log"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # Redis settings
    REDIS_HOST: str = ""
    REDIS_USER: str = ""
    REDIS_PASSWORD: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # CORS settings
    CORS_ORIGINS: str = "*"  # Comma-separated list of allowed origins

    # PostgreSQL settings
    POSTGRESQL_USER: str = ""
    POSTGRESQL_PASSWORD: str = ""
    POSTGRESQL_HOST: str = ""
    POSTGRESQL_PORT: int = 5432
    POSTGRESQL_DB: str = ""
    POSTGRESQL_POOL_SIZE: int = 5
    POSTGRESQL_MAX_OVERFLOW: int = 10
    POSTGRESQL_URI: str = f"postgresql://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DB}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
