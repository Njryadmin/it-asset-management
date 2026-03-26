from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "IT Asset Management"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "itasset"
    POSTGRES_PORT: str = "5432"
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Build DATABASE_URL
if not settings.DATABASE_URL:
    settings.DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

if not settings.REDIS_URL:
    settings.REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
