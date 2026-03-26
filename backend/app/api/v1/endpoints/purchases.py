from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models import PurchaseRequest, PurchaseRequestStatus, User
from app.schemas.schemas import (
    PurchaseRequestCreate, PurchaseRequestUpdate,
    PurchaseRequestResponse, PurchaseRequestListResponse
)
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/purchase-requests", tags=["采购管理"])


@router.get("")
async def list_purchase_requests(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = select(PurchaseRequest)
    
    if keyword:
        query = query.where(
            PurchaseRequest.title.ilike(f"%{keyword}%") |
            PurchaseRequest.description.ilike(f"%{keyword}%")
        )
    if status:
        query = query.where(PurchaseRequest.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {"total": total, "items": items}


@router.get("/pending")
async def list_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取待审批的采购申请"""
    query = select(PurchaseRequest).where(
        PurchaseRequest.status == PurchaseRequestStatus.PENDING
    ).order_by(PurchaseRequest.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()
    return items


@router.get("/{request_id}")
async def get_purchase_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    return purchase_request


@router.post("")
async def create_purchase_request(
    request_in: PurchaseRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    purchase_request = PurchaseRequest(
        **request_in.model_dump(),
        requester_id=current_user.id,
        status=PurchaseRequestStatus.DRAFT
    )
    db.add(purchase_request)
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.put("/{request_id}")
async def update_purchase_request(
    request_id: int,
    request_in: PurchaseRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    # Only requester can update draft
    if purchase_request.requester_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限修改此申请")
    
    update_data = request_in.model_dump(exclude_unset=True)
    
    # Validate status enum if provided
    if 'status' in update_data:
        try:
            update_data['status'] = PurchaseRequestStatus(update_data['status'])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的采购状态: {update_data['status']}")
    
    for key, value in update_data.items():
        setattr(purchase_request, key, value)
    
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.post("/{request_id}/submit")
async def submit_purchase_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """提交采购申请"""
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    if purchase_request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此申请")
    
    if purchase_request.status != PurchaseRequestStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能提交草稿状态的申请")
    
    purchase_request.status = PurchaseRequestStatus.PENDING
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.post("/{request_id}/approve")
async def approve_purchase_request(
    request_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """审批通过采购申请（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以审批")
    
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    if purchase_request.status != PurchaseRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能审批待处理状态的申请")
    
    purchase_request.status = PurchaseRequestStatus.APPROVED
    purchase_request.approver_comment = comment
    purchase_request.approved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.post("/{request_id}/reject")
async def reject_purchase_request(
    request_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """拒绝采购申请（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以审批")
    
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    if purchase_request.status != PurchaseRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能拒绝待处理状态的申请")
    
    purchase_request.status = PurchaseRequestStatus.REJECTED
    purchase_request.approver_comment = comment
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.post("/{request_id}/purchase")
async def mark_as_purchased(
    request_id: int,
    actual_price: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记为已采购（仅管理员）"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以操作")
    
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    if purchase_request.status != PurchaseRequestStatus.APPROVED:
        raise HTTPException(status_code=400, detail="只能标记已审批的申请")
    
    purchase_request.status = PurchaseRequestStatus.PURCHASED
    if actual_price is not None:
        purchase_request.actual_price = actual_price
    purchase_request.purchased_at = datetime.utcnow()
    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.delete("/{request_id}")
async def delete_purchase_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除采购申请（仅草稿状态）"""
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")
    
    if purchase_request.requester_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="无权限删除此申请")
    
    if purchase_request.status != PurchaseRequestStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能删除草稿状态的申请")
    
    await db.delete(purchase_request)
    await db.commit()
    return {"message": "删除成功"}
