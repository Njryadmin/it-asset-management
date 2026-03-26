from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import init_db
from app.core.redis import init_redis, close_redis
from app.api.v1.router import api_router
from app.services.init_db import init_sample_data


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    # Mount static files for uploads
    os.makedirs("/app/static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="/app/static"), name="static")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup
    @app.on_event("startup")
    async def startup_event():
        await init_db()
        await init_sample_data()
        await init_redis()

    # Shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_redis()

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app


app = create_app()
