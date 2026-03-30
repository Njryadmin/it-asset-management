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
    SECRET_KEY: str = ""  # Must be set via env or will be auto-generated
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Security
    ALLOW_PUBLIC_REGISTRATION: bool = False  # Set to True only if public registration is needed
    LOGIN_RATE_LIMIT: str = "5/minute"  # Brute force protection

    # CORS - should be overridden via BACKEND_CORS_ORIGINS env var in production
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3030",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


_settings = Settings()

# SECURITY: Generate SECRET_KEY at runtime if not provided via environment variable
# This ensures each startup gets a unique key. For production, always set SECRET_KEY env var.
if not _settings.SECRET_KEY:
    _settings.SECRET_KEY = secrets.token_urlsafe(32)
    print("WARNING: SECRET_KEY auto-generated at runtime. Set SECRET_KEY env var for production!")

settings = _settings

# Build DATABASE_URL
if not settings.DATABASE_URL:
    settings.DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

if not settings.REDIS_URL:
    settings.REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
