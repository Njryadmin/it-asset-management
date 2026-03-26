from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.database import get_db
from app.models import Asset, AssetStatus
from app.schemas.schemas import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/assets", tags=["资产管理"])


@router.get("")
async def list_assets(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="资产状态"),
    department_id: Optional[int] = Query(None, description="部门ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = select(Asset)
    
    if keyword:
        query = query.where(
            Asset.name.ilike(f"%{keyword}%") |
            Asset.asset_code.ilike(f"%{keyword}%") |
            Asset.serial_number.ilike(f"%{keyword}%")
        )
    if category_id is not None:
        query = query.where(Asset.category_id == category_id)
    if status:
        query = query.where(Asset.status == status)
    if department_id is not None:
        query = query.where(Asset.department_id == department_id)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {"total": total, "items": items}


@router.get("/stats")
async def get_asset_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取资产统计"""
    # Total count
    total_result = await db.execute(select(func.count()).select_from(Asset))
    total = total_result.scalar()
    
    # Count by status
    status_result = await db.execute(
        select(Asset.status, func.count(Asset.id))
        .group_by(Asset.status)
    )
    by_status = {row[0].value: row[1] for row in status_result.all()}
    
    # Count by category
    category_result = await db.execute(
        select(Asset.category_id, func.count(Asset.id))
        .group_by(Asset.category_id)
    )
    by_category = {str(row[0]): row[1] for row in category_result.all()}
    
    return {
        "total": total,
        "by_status": by_status,
        "by_category": by_category
    }


@router.get("/{asset_id}")
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    return asset


@router.post("")
async def create_asset(
    asset_in: AssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Check if asset_code exists
    result = await db.execute(select(Asset).where(Asset.asset_code == asset_in.asset_code))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="资产编号已存在")
    
    if asset_in.serial_number:
        result = await db.execute(select(Asset).where(Asset.serial_number == asset_in.serial_number))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="序列号已存在")
    
    asset = Asset(**asset_in.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.put("/{asset_id}")
async def update_asset(
    asset_id: int,
    asset_in: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    
    if asset_in.asset_code and asset_in.asset_code != asset.asset_code:
        check_result = await db.execute(
            select(Asset).where(Asset.asset_code == asset_in.asset_code, Asset.id != asset_id)
        )
        if check_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="资产编号已存在")
    
    if asset_in.serial_number and asset_in.serial_number != asset.serial_number:
        check_result = await db.execute(
            select(Asset).where(Asset.serial_number == asset_in.serial_number, Asset.id != asset_id)
        )
        if check_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="序列号已存在")
    
    for key, value in asset_in.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    
    await db.delete(asset)
    await db.commit()
    return {"message": "删除成功"}
