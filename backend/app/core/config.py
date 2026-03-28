from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os


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
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://192.168.10.1:3030",
        "http://127.0.0.1:3030",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# SECURITY: If SECRET_KEY is default and not set via env, use a stable default for development
# In production, always set SECRET_KEY environment variable
if settings.SECRET_KEY == "your-secret-key-change-in-production":
    # Use a stable default for development - NOT recommended for production
    settings.SECRET_KEY = "it-asset-mgmt-dev-secret-key-do-not-use-in-production"

# Build DATABASE_URL
if not settings.DATABASE_URL:
    settings.DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

if not settings.REDIS_URL:
    settings.REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
