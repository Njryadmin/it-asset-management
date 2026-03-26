from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, suppliers, departments, assets, purchases, dashboard, users, settings

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(suppliers.router)
api_router.include_router(departments.router)
api_router.include_router(assets.router)
api_router.include_router(purchases.router)
api_router.include_router(dashboard.router)
api_router.include_router(users.router)
api_router.include_router(settings.router)
