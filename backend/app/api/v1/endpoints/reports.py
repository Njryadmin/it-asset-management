from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.models import Asset, PurchaseRequest, Category, Department, Supplier
from app.api.v1.endpoints.auth import get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["报表"])


class DistributionItem(BaseModel):
    name: str
    value: int


class AssetSummaryResponse(BaseModel):
    total: int
    by_status: dict
    by_category: list[DistributionItem]
    by_department: list[DistributionItem]
    by_importance: dict
    this_month_new: int
    this_month_retired: int


class DistributionResponse(BaseModel):
    by_category: list[DistributionItem]
    by_status: list[DistributionItem]
    by_department: list[DistributionItem]
    by_importance: list[DistributionItem]


class TrendItem(BaseModel):
    month: str
    added: int
    retired: int


class TrendResponse(BaseModel):
    items: list[TrendItem]


class PurchaseSummaryResponse(BaseModel):
    total_count: int
    total_amount: float
    by_status: dict
    by_supplier: list[DistributionItem]
    this_month_count: int
    this_month_amount: float


@router.get("/assets/summary", response_model=AssetSummaryResponse)
async def get_asset_summary(
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Total
    total = await db.scalar(
        select(func.count(Asset.id)).where(Asset.deleted_at.is_(None))
    ) or 0

    # By status
    status_result = await db.execute(
        select(Asset.status, func.count(Asset.id))
        .where(Asset.deleted_at.is_(None))
        .group_by(Asset.status)
    )
    by_status = {str(row[0].value): row[1] for row in status_result.all()}

    # By category
    cat_result = await db.execute(
        select(Category.name, func.count(Asset.id))
        .join(Asset, Asset.category_id == Category.id)
        .where(Asset.deleted_at.is_(None))
        .group_by(Category.name)
    )
    by_category = [DistributionItem(name=str(row[0]), value=row[1]) for row in cat_result.all()]

    # By department
    dept_result = await db.execute(
        select(Department.name, func.count(Asset.id))
        .join(Asset, Asset.department_id == Department.id)
        .where(Asset.deleted_at.is_(None))
        .group_by(Department.name)
    )
    by_department = [DistributionItem(name=str(row[0]), value=row[1]) for row in dept_result.all()]

    # By importance
    imp_result = await db.execute(
        select(Asset.importance_level, func.count(Asset.id))
        .where(
            Asset.deleted_at.is_(None),
            Asset.importance_level.isnot(None)
        )
        .group_by(Asset.importance_level)
    )
    by_importance = {str(row[0] or "未分类"): row[1] for row in imp_result.all()}

    # This month new
    now = datetime.now()
    this_month_new = await db.scalar(
        select(func.count(Asset.id)).where(
            Asset.deleted_at.is_(None),
            func.extract("year", Asset.created_at) == now.year,
            func.extract("month", Asset.created_at) == now.month,
        )
    ) or 0

    # This month retired
    this_month_retired = await db.scalar(
        select(func.count(Asset.id)).where(
            Asset.deleted_at.is_(None),
            Asset.status.value == "RETIRED",
            func.extract("year", Asset.updated_at) == now.year,
            func.extract("month", Asset.updated_at) == now.month,
        )
    ) or 0

    return AssetSummaryResponse(
        total=total,
        by_status=by_status,
        by_category=by_category,
        by_department=by_department,
        by_importance=by_importance,
        this_month_new=this_month_new,
        this_month_retired=this_month_retired,
    )


@router.get("/assets/distribution", response_model=DistributionResponse)
async def get_asset_distribution(
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # By category
    cat_result = await db.execute(
        select(Category.name, func.count(Asset.id))
        .join(Asset, Asset.category_id == Category.id)
        .where(Asset.deleted_at.is_(None))
        .group_by(Category.name)
    )
    by_category = [DistributionItem(name=str(row[0]), value=row[1]) for row in cat_result.all()]

    # By status
    status_result = await db.execute(
        select(Asset.status, func.count(Asset.id))
        .where(Asset.deleted_at.is_(None))
        .group_by(Asset.status)
    )
    by_status = [DistributionItem(name=str(row[0].value), value=row[1]) for row in status_result.all()]

    # By department
    dept_result = await db.execute(
        select(Department.name, func.count(Asset.id))
        .join(Asset, Asset.department_id == Department.id)
        .where(Asset.deleted_at.is_(None))
        .group_by(Department.name)
    )
    by_department = [DistributionItem(name=str(row[0]), value=row[1]) for row in dept_result.all()]

    # By importance
    imp_result = await db.execute(
        select(Asset.importance_level, func.count(Asset.id))
        .where(
            Asset.deleted_at.is_(None),
            Asset.importance_level.isnot(None)
        )
        .group_by(Asset.importance_level)
    )
    by_importance = [DistributionItem(name=str(row[0] or "未分类"), value=row[1]) for row in imp_result.all()]

    return DistributionResponse(
        by_category=by_category,
        by_status=by_status,
        by_department=by_department,
        by_importance=by_importance,
    )


@router.get("/assets/trend", response_model=TrendResponse)
async def get_asset_trend(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    now = datetime.now()
    items = []
    for i in range(months - 1, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        month_str = f"{y}-{m:02d}"

        added = await db.scalar(
            select(func.count(Asset.id)).where(
                Asset.deleted_at.is_(None),
                func.extract("year", Asset.created_at) == y,
                func.extract("month", Asset.created_at) == m,
            )
        ) or 0

        retired = await db.scalar(
            select(func.count(Asset.id)).where(
                Asset.deleted_at.is_(None),
                Asset.status.value == "RETIRED",
                func.extract("year", Asset.updated_at) == y,
                func.extract("month", Asset.updated_at) == m,
            )
        ) or 0

        items.append(TrendItem(month=month_str, added=added, retired=retired))

    return TrendResponse(items=items)


@router.get("/purchases/summary", response_model=PurchaseSummaryResponse)
async def get_purchase_summary(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Count
    total_count = await db.scalar(select(func.count(PurchaseRequest.id))) or 0

    # Amount sum
    amount_result = await db.execute(select(PurchaseRequest.estimated_price))
    amount_rows = amount_result.scalars().all()
    total_amount = sum(r or 0 for r in amount_rows)

    # By status
    status_result = await db.execute(
        select(PurchaseRequest.status, func.count(PurchaseRequest.id)).group_by(PurchaseRequest.status)
    )
    by_status = {str(row[0].value): row[1] for row in status_result.all()}

    # By supplier (top 10)
    supplier_result = await db.execute(
        select(Supplier.name, func.count(PurchaseRequest.id))
        .join(Supplier, PurchaseRequest.supplier_id == Supplier.id)
        .group_by(Supplier.name)
        .limit(10)
    )
    by_supplier = [DistributionItem(name=str(row[0]), value=row[1]) for row in supplier_result.all()]

    # This month
    now = datetime.now()
    this_month_count = await db.scalar(
        select(func.count(PurchaseRequest.id)).where(
            func.extract("year", PurchaseRequest.created_at) == now.year,
            func.extract("month", PurchaseRequest.created_at) == now.month,
        )
    ) or 0

    month_result = await db.execute(
        select(PurchaseRequest.estimated_price).where(
            func.extract("year", PurchaseRequest.created_at) == now.year,
            func.extract("month", PurchaseRequest.created_at) == now.month,
        )
    )
    month_amount_rows = month_result.scalars().all()
    this_month_amount = sum(r or 0 for r in month_amount_rows)

    return PurchaseSummaryResponse(
        total_count=total_count,
        total_amount=total_amount,
        by_status=by_status,
        by_supplier=by_supplier,
        this_month_count=this_month_count,
        this_month_amount=this_month_amount,
    )
