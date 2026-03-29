from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models import User
from app.models.maintenance_log import AssetMaintenanceLog
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/asset-maintenance-logs", tags=["维保记录"])


# ============ Schemas ============
class MaintenanceLogCreate(BaseModel):
    asset_id: int
    maintenance_type: str
    maintenance_date: date
    vendor: Optional[str] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    next_maintenance_date: Optional[date] = None


class MaintenanceLogUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    maintenance_date: Optional[date] = None
    vendor: Optional[str] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    next_maintenance_date: Optional[date] = None


class MaintenanceLogResponse(BaseModel):
    id: int
    asset_id: int
    maintenance_type: str
    maintenance_date: date
    vendor: Optional[str]
    cost: Optional[float]
    description: Optional[str]
    next_maintenance_date: Optional[date]
    created_by: Optional[int]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaintenanceLogListResponse(BaseModel):
    total: int
    items: List[MaintenanceLogResponse]


# ============ Endpoints ============
@router.get("", response_model=MaintenanceLogListResponse)
async def list_maintenance_logs(
    asset_id: int = Query(..., description="资产ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取维保记录列表（按资产ID筛选，分页）"""
    query = select(AssetMaintenanceLog).where(AssetMaintenanceLog.asset_id == asset_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Order by maintenance_date desc
    query = query.order_by(AssetMaintenanceLog.maintenance_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "items": items}


@router.post("", response_model=MaintenanceLogResponse)
async def create_maintenance_log(
    data: MaintenanceLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建维保记录（管理员）"""
    log = AssetMaintenanceLog(**data.model_dump())
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


@router.put("/{log_id}", response_model=MaintenanceLogResponse)
async def update_maintenance_log(
    log_id: int,
    data: MaintenanceLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新维保记录（管理员）"""
    result = await db.execute(select(AssetMaintenanceLog).where(AssetMaintenanceLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="维保记录不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(log, key, value)

    await db.commit()
    await db.refresh(log)
    return log


@router.delete("/{log_id}")
async def delete_maintenance_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除维保记录"""
    result = await db.execute(select(AssetMaintenanceLog).where(AssetMaintenanceLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="维保记录不存在")

    await db.delete(log)
    await db.commit()
    return {"message": "删除成功"}
