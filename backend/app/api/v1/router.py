from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, suppliers, departments, assets, purchases, dashboard, users, settings, audit_logs, approvals, reports, maintenance, asset_transfers, reminders, depreciation

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
api_router.include_router(audit_logs.router)
api_router.include_router(approvals.router, tags=["审批管理"])
api_router.include_router(approvals.approval_flows_router, tags=["审批流程"])
api_router.include_router(reports.router, tags=["报表"])
api_router.include_router(maintenance.router)
api_router.include_router(asset_transfers.router, tags=["资产转移"])
api_router.include_router(reminders.router, tags=["提醒"])
api_router.include_router(depreciation.router, tags=["资产折旧"])
