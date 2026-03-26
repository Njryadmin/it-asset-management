from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models import Supplier
from app.schemas.schemas import SupplierCreate, SupplierUpdate, SupplierResponse
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/suppliers", tags=["供应商管理"])


@router.get("")
async def list_suppliers(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = select(Supplier)
    
    if keyword:
        query = query.where(
            Supplier.name.ilike(f"%{keyword}%") |
            Supplier.code.ilike(f"%{keyword}%") |
            Supplier.contact_person.ilike(f"%{keyword}%")
        )
    if is_active is not None:
        query = query.where(Supplier.is_active == is_active)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {"total": total, "items": items}


@router.get("/{supplier_id}")
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier


@router.post("")
async def create_supplier(
    supplier_in: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    if supplier_in.code:
        result = await db.execute(select(Supplier).where(Supplier.code == supplier_in.code))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="供应商代码已存在")
    
    supplier = Supplier(**supplier_in.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}")
async def update_supplier(
    supplier_id: int,
    supplier_in: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    for key, value in supplier_in.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    await db.delete(supplier)
    await db.commit()
    return {"message": "删除成功"}
