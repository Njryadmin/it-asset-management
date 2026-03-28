from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.sql import lte, gte
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.models import User, Asset, AssetMaintenanceLog, SystemSettings
from app.schemas.schemas import Token

router = APIRouter(prefix="/reminders", tags=["提醒"])


@router.get("/warranty-expiring")
async def get_warranty_expiring_assets(
    days: int = Query(30, ge=1, le=365, description="提前提醒天数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取即将过保的资产"""
    today = datetime.utcnow().date()
    expire_threshold = today + timedelta(days=days)
    
    result = await db.execute(
        select(Asset).where(
            Asset.warranty_expire_date.isnot(None),
            Asset.warranty_expire_date >= today,
            Asset.warranty_expire_date <= expire_threshold,
            Asset.status.in_(["in_use", "idle"])
        ).order_by(Asset.warranty_expire_date)
    )
    assets = result.scalars().all()
    
    return {
        "total": len(assets),
        "items": [
            {
                "id": a.id,
                "name": a.name,
                "assetCode": a.asset_code,
                "warrantyExpireDate": a.warranty_expire_date.isoformat() if a.warranty_expire_date else None,
                "daysRemaining": (a.warranty_expire_date - today).days if a.warranty_expire_date else None,
                "status": a.status.value if hasattr(a.status, 'value') else a.status
            }
            for a in assets
        ]
    }


@router.get("/maintenance-due")
async def get_maintenance_due(
    days: int = Query(30, ge=1, le=365, description="提前提醒天数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取即将需要维保的资产"""
    today = datetime.utcnow().date()
    due_threshold = today + timedelta(days=days)
    
    # Get assets with upcoming maintenance
    result = await db.execute(
        select(AssetMaintenanceLog, Asset)
        .join(Asset, AssetMaintenanceLog.asset_id == Asset.id)
        .where(
            AssetMaintenanceLog.next_maintenance_date.isnot(None),
            AssetMaintenanceLog.next_maintenance_date >= today,
            AssetMaintenanceLog.next_maintenance_date <= due_threshold
        ).order_by(AssetMaintenanceLog.next_maintenance_date)
    )
    rows = result.all()
    
    items = []
    for log, asset in rows:
        items.append({
            "id": asset.id,
            "name": asset.name,
            "assetCode": asset.asset_code,
            "maintenanceType": log.maintenance_type,
            "nextMaintenanceDate": log.next_maintenance_date.isoformat() if log.next_maintenance_date else None,
            "daysRemaining": (log.next_maintenance_date - today).days if log.next_maintenance_date else None,
            "lastMaintenanceDate": log.maintenance_date.isoformat() if log.maintenance_date else None,
            "lastMaintenanceVendor": log.vendor
        })
    
    return {"total": len(items), "items": items}


@router.get("/summary")
async def get_reminder_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取提醒摘要（仪表盘用）"""
    today = datetime.utcnow().date()
    expire_7_days = today + timedelta(days=7)
    expire_30_days = today + timedelta(days=30)
    
    # Count assets expiring in 7 days
    result_7 = await db.execute(
        select(func.count(Asset.id)).where(
            Asset.warranty_expire_date.isnot(None),
            Asset.warranty_expire_date >= today,
            Asset.warranty_expire_date <= expire_7_days
        )
    )
    expiring_7 = result_7.scalar() or 0
    
    # Count assets expiring in 30 days
    result_30 = await db.execute(
        select(func.count(Asset.id)).where(
            Asset.warranty_expire_date.isnot(None),
            Asset.warranty_expire_date >= today,
            Asset.warranty_expire_date <= expire_30_days
        )
    )
    expiring_30 = result_30.scalar() or 0
    
    # Count maintenance due in 30 days
    result_maint = await db.execute(
        select(func.count(AssetMaintenanceLog.id)).where(
            AssetMaintenanceLog.next_maintenance_date.isnot(None),
            AssetMaintenanceLog.next_maintenance_date >= today,
            AssetMaintenanceLog.next_maintenance_date <= expire_30_days
        )
    )
    maintenance_due = result_maint.scalar() or 0
    
    return {
        "warrantyExpiring7Days": expiring_7,
        "warrantyExpiring30Days": expiring_30,
        "maintenanceDue30Days": maintenance_due
    }
