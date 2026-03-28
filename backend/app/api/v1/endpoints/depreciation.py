from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from app.core.database import get_db
from app.core.permissions import get_current_active_user
from app.models import User, Asset

router = APIRouter(prefix="/depreciation", tags=["资产折旧"])


def calculate_straight_line(purchase_price: float, purchase_date: date, now: date,
                             years: int, salvage_rate: float) -> dict:
    """直线法折旧"""
    if not purchase_price or purchase_price <= 0:
        return {"originalValue": 0, "currentValue": 0, "accumulatedDepreciation": 0,
                "depreciationRate": 0, "usedYears": 0, "netValueRate": 0}
    
    salvage_value = purchase_price * salvage_rate
    depreciable_amount = purchase_price - salvage_value
    annual_depreciation = depreciable_amount / years if years > 0 else 0
    
    # 计算已使用月份
    days_used = (now - purchase_date).days
    months_used = days_used / 30.0
    years_used = months_used / 12.0
    
    accumulated = min(annual_depreciation * years_used, depreciable_amount)
    current_value = max(purchase_price - accumulated, salvage_value)
    
    return {
        "originalValue": round(purchase_price, 2),
        "currentValue": round(current_value, 2),
        "accumulatedDepreciation": round(accumulated, 2),
        "depreciationRate": round(accumulated / purchase_price * 100, 2) if purchase_price else 0,
        "usedYears": round(years_used, 2),
        "netValueRate": round(current_value / purchase_price * 100, 2) if purchase_price else 0,
        "annualDepreciation": round(annual_depreciation, 2),
        "salvageValue": round(salvage_value, 2),
        "remainingYears": round(max(years - years_used, 0), 2)
    }


def calculate_declining_balance(purchase_price: float, purchase_date: date, now: date,
                                 years: int, salvage_rate: float) -> dict:
    """双倍余额递减法折旧"""
    if not purchase_price or purchase_price <= 0:
        return {"originalValue": 0, "currentValue": 0, "accumulatedDepreciation": 0,
                "depreciationRate": 0, "usedYears": 0, "netValueRate": 0}
    
    salvage_value = purchase_price * salvage_rate
    rate = (1 / years * 2) if years > 0 else 0  # 双倍折旧率
    
    days_used = (now - purchase_date).days
    years_used = days_used / 365.0
    
    accumulated = 0
    book_value = purchase_price
    year = 0
    while year < years and year < int(years_used) + 1:
        if book_value <= salvage_value:
            break
        d = book_value * rate
        if book_value - d < salvage_value:
            d = book_value - salvage_value
        accumulated += d
        book_value -= d
        year += 1
    
    current_value = max(book_value, salvage_value)
    
    return {
        "originalValue": round(purchase_price, 2),
        "currentValue": round(current_value, 2),
        "accumulatedDepreciation": round(accumulated, 2),
        "depreciationRate": round(accumulated / purchase_price * 100, 2) if purchase_price else 0,
        "usedYears": round(years_used, 2),
        "netValueRate": round(current_value / purchase_price * 100, 2) if purchase_price else 0,
        "salvageValue": round(salvage_value, 2),
        "remainingYears": round(max(years - years_used, 0), 2)
    }


@router.get("/asset/{asset_id}")
async def calculate_asset_depreciation(
    asset_id: int,
    as_of_date: Optional[str] = Query(None, description="计算日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """计算单个资产的折旧"""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        return {"error": "资产不存在"}
    
    now = datetime.strptime(as_of_date, "%Y-%m-%d").date() if as_of_date else date.today()
    
    purchase_date = asset.purchase_date
    if isinstance(purchase_date, datetime):
        purchase_date = purchase_date.date()
    
    if not purchase_date:
        return {"error": "资产无购买日期"}
    
    years = asset.depreciation_years or 5
    method = asset.depreciation_method or "straight-line"
    salvage = asset.salvage_rate if asset.salvage_rate is not None else 0.05
    
    if method == "declining-balance":
        calc_result = calculate_declining_balance(
            asset.purchase_price or 0, purchase_date, now, years, salvage
        )
    else:
        calc_result = calculate_straight_line(
            asset.purchase_price or 0, purchase_date, now, years, salvage
        )
    
    return {
        "assetId": asset.id,
        "assetName": asset.name,
        "assetCode": asset.asset_code,
        "purchaseDate": purchase_date.isoformat(),
        "asOfDate": now.isoformat(),
        "method": method,
        "depreciationYears": years,
        "salvageRate": salvage,
        **calc_result
    }


@router.get("/list")
async def list_depreciation(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    as_of_date: Optional[str] = Query(None, description="计算日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量计算资产折旧"""
    now = datetime.strptime(as_of_date, "%Y-%m-%d").date() if as_of_date else date.today()
    
    query = select(Asset).where(
        Asset.purchase_price.isnot(None),
        Asset.purchase_price > 0,
        Asset.purchase_date.isnot(None),
        Asset.status.in_(["in_use", "idle"])
    )
    
    if keyword:
        query = query.where(Asset.name.contains(keyword) | Asset.asset_code.contains(keyword))
    
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    items = []
    total_original = 0
    total_current = 0
    total_accumulated = 0
    
    for asset in assets:
        purchase_date = asset.purchase_date
        if isinstance(purchase_date, datetime):
            purchase_date = purchase_date.date()
        
        years = asset.depreciation_years or 5
        method = asset.depreciation_method or "straight-line"
        salvage = asset.salvage_rate if asset.salvage_rate is not None else 0.05
        
        if method == "declining-balance":
            calc = calculate_declining_balance(asset.purchase_price, purchase_date, now, years, salvage)
        else:
            calc = calculate_straight_line(asset.purchase_price, purchase_date, now, years, salvage)
        
        items.append({
            "assetId": asset.id,
            "assetName": asset.name,
            "assetCode": asset.asset_code,
            "purchaseDate": purchase_date.isoformat() if purchase_date else None,
            "asOfDate": now.isoformat(),
            "method": method,
            "depreciationYears": years,
            **calc
        })
        
        total_original += calc["originalValue"]
        total_current += calc["currentValue"]
        total_accumulated += calc["accumulatedDepreciation"]
    
    return {
        "items": items,
        "total": len(items),
        "summary": {
            "totalOriginalValue": round(total_original, 2),
            "totalCurrentValue": round(total_current, 2),
            "totalAccumulatedDepreciation": round(total_accumulated, 2),
            "totalDepreciationRate": round(total_accumulated / total_original * 100, 2) if total_original else 0
        }
    }
