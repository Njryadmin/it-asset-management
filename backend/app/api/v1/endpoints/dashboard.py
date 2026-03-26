from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import Asset, Category, Supplier, Department, User, PurchaseRequest, PurchaseRequestStatus
from app.schemas.schemas import DashboardStats, AssetResponse, PurchaseRequestResponse
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Total counts
    total_assets = await db.scalar(select(func.count(Asset.id)))
    total_categories = await db.scalar(select(func.count(Category.id)))
    total_suppliers = await db.scalar(select(func.count(Supplier.id)))
    total_departments = await db.scalar(select(func.count(Department.id)))
    total_users = await db.scalar(select(func.count(User.id)))
    total_purchase_requests = await db.scalar(select(func.count(PurchaseRequest.id)))
    
    # Assets by status
    status_result = await db.execute(
        select(Asset.status, func.count(Asset.id)).group_by(Asset.status)
    )
    assets_by_status = {row[0].value: row[1] for row in status_result.all()}
    
    # Assets by category
    category_result = await db.execute(
        select(Category.name, func.count(Asset.id))
        .join(Asset, Asset.category_id == Category.id)
        .group_by(Category.name)
    )
    assets_by_category = {row[0]: row[1] for row in category_result.all()}
    
    # Recent assets (last 10)
    recent_result = await db.execute(
        select(Asset).order_by(Asset.created_at.desc()).limit(10)
    )
    recent_assets = recent_result.scalars().all()
    
    # Pending purchase requests
    pending_result = await db.execute(
        select(PurchaseRequest)
        .where(PurchaseRequest.status == PurchaseRequestStatus.PENDING)
        .order_by(PurchaseRequest.created_at.desc())
        .limit(10)
    )
    pending_purchase_requests = pending_result.scalars().all()
    
    return DashboardStats(
        total_assets=total_assets or 0,
        total_categories=total_categories or 0,
        total_suppliers=total_suppliers or 0,
        total_departments=total_departments or 0,
        total_users=total_users or 0,
        total_purchase_requests=total_purchase_requests or 0,
        assets_by_status=assets_by_status,
        assets_by_category=assets_by_category,
        recent_assets=recent_assets,
        pending_purchase_requests=pending_purchase_requests
    )
