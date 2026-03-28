from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models import PurchaseRequest, PurchaseRequestStatus, User, Asset, AssetStatus
from app.models.approval_flow import ApprovalFlow
from app.models.approval_instance import ApprovalInstance
from app.schemas.schemas import (
    PurchaseRequestCreate, PurchaseRequestUpdate,
    PurchaseRequestResponse, PurchaseRequestListResponse
)
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/purchase-requests", tags=["采购管理"])


async def generate_instance_no(db: AsyncSession, prefix: str = "APR") -> str:
    """Generate a unique instance number like APR-2026-00001"""
    year = datetime.utcnow().year
    # Get the count for this year
    result = await db.execute(
        select(func.count()).select_from(ApprovalInstance)
        .where(ApprovalInstance.instance_no.like(f"{prefix}-{year}-%"))
    )
    count = result.scalar() or 0
    return f"{prefix}-{year}-{str(count + 1).zfill(5)}"


async def get_default_purchase_flow(db: AsyncSession) -> Optional[ApprovalFlow]:
    """Get the default purchase request approval flow"""
    result = await db.execute(
        select(ApprovalFlow).where(
            ApprovalFlow.applicable_to == "purchase_request",
            ApprovalFlow.is_active == True
        ).order_by(ApprovalFlow.id).limit(1)
    )
    return result.scalar_one_or_none()


async def generate_asset_code(db: AsyncSession) -> str:
    """Generate a unique asset code like AST-202603-001"""
    now = datetime.utcnow()
    prefix = now.strftime("%Y%m")
    result = await db.execute(
        select(func.max(Asset.asset_code)).where(Asset.asset_code.like(f"AST-{prefix}%"))
    )
    last = result.scalar() or f"AST-{prefix}000"
    seq = int(last.split("-")[-1]) + 1
    return f"AST-{prefix}{seq:03d}"


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
    current_user: User = Depends(require_admin)
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
    current_user: User = Depends(require_admin)
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
    current_user: User = Depends(require_admin)
):
    """提交采购申请并创建审批实例"""
    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")

    if purchase_request.requester_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此申请")

    if purchase_request.status != PurchaseRequestStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能提交草稿状态的申请")

    # Get default approval flow
    flow = await get_default_purchase_flow(db)
    if not flow:
        raise HTTPException(status_code=400, detail="未配置审批流程，请先创建采购审批流程")

    # Create approval instance
    total_steps = len(flow.steps) if flow.steps else 1
    instance_no = await generate_instance_no(db)

    approval_instance = ApprovalInstance(
        flow_id=flow.id,
        instance_no=instance_no,
        biz_type="purchase_request",
        biz_id=purchase_request.id,
        applicant_id=current_user.id,
        applicant_name=current_user.full_name or current_user.username,
        current_step=1,
        status="pending",
        approval_chain=[],
        total_steps=total_steps,
    )
    db.add(approval_instance)

    purchase_request.status = PurchaseRequestStatus.PENDING
    await db.commit()
    await db.refresh(purchase_request)
    await db.refresh(approval_instance)
    return {
        "purchase_request": purchase_request,
        "approval_instance": {
            "id": approval_instance.id,
            "instance_no": approval_instance.instance_no,
            "status": approval_instance.status,
            "current_step": approval_instance.current_step,
            "total_steps": approval_instance.total_steps,
        }
    }


@router.post("/{request_id}/approve")
async def approve_purchase_request(
    request_id: int,
    comment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """审批通过采购申请（仅管理员）- 通过审批实例工作流"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以审批")

    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")

    if purchase_request.status != PurchaseRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能审批待处理状态的申请")

    # Find corresponding approval instance
    instance_result = await db.execute(
        select(ApprovalInstance).where(
            ApprovalInstance.biz_type == "purchase_request",
            ApprovalInstance.biz_id == purchase_request.id,
            ApprovalInstance.status == "pending"
        )
    )
    instance = instance_result.scalar_one_or_none()

    if instance:
        # Record approval
        approval_record = {
            "step": instance.current_step,
            "approver": current_user.full_name or current_user.username,
            "approver_id": current_user.id,
            "action": "approve",
            "comment": comment,
            "time": datetime.utcnow().isoformat(),
        }
        chain = list(instance.approval_chain or [])
        chain.append(approval_record)
        instance.approval_chain = chain

        # Check if all steps completed
        if instance.total_steps and instance.current_step >= instance.total_steps:
            instance.status = "approved"
            purchase_request.status = PurchaseRequestStatus.APPROVED
            purchase_request.approver_comment = comment
            purchase_request.approved_at = datetime.utcnow()
        else:
            instance.current_step += 1

    else:
        # Fallback: direct approval if no instance exists (backward compatibility)
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
    """拒绝采购申请（仅管理员）- 通过审批实例工作流"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="只有管理员可以审批")

    result = await db.execute(select(PurchaseRequest).where(PurchaseRequest.id == request_id))
    purchase_request = result.scalar_one_or_none()
    if not purchase_request:
        raise HTTPException(status_code=404, detail="采购申请不存在")

    if purchase_request.status != PurchaseRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="只能拒绝待处理状态的申请")

    # Find corresponding approval instance
    instance_result = await db.execute(
        select(ApprovalInstance).where(
            ApprovalInstance.biz_type == "purchase_request",
            ApprovalInstance.biz_id == purchase_request.id,
            ApprovalInstance.status == "pending"
        )
    )
    instance = instance_result.scalar_one_or_none()

    if instance:
        # Record rejection
        approval_record = {
            "step": instance.current_step,
            "approver": current_user.full_name or current_user.username,
            "approver_id": current_user.id,
            "action": "reject",
            "comment": comment,
            "time": datetime.utcnow().isoformat(),
        }
        chain = list(instance.approval_chain or [])
        chain.append(approval_record)
        instance.approval_chain = chain
        instance.status = "rejected"

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
    """标记为已采购（仅管理员）- 同时自动在资产表中创建资产记录"""
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

    # ── 自动创建资产记录 ──────────────────────────────────────────────
    asset_code = await generate_asset_code(db)
    asset = Asset(
        name=purchase_request.title,
        asset_code=asset_code,
        category_id=purchase_request.category_id,
        supplier_id=purchase_request.supplier_id,
        department_id=getattr(purchase_request, 'department_id', None),
        purchase_date=datetime.utcnow().date(),
        purchase_price=purchase_request.actual_price or purchase_request.estimated_price,
        status=AssetStatus.IDLE,
        description=f"来源于采购申请单：{purchase_request.title} (ID: {purchase_request.id})",
    )
    db.add(asset)
    await db.flush()  # 获取 asset.id

    # 写入审计日志
    from app.services.audit_service import log_action
    await log_action(
        db=db,
        biz_type="assets",
        biz_id=asset.id,
        action="CREATE",
        actor=current_user,
        before=None,
        after={"id": asset.id, "name": asset.name, "asset_code": asset.asset_code},
        asset_code=asset.asset_code,
        summary=f"采购入库自动创建：{asset.name}",
    )
    # ─────────────────────────────────────────────────────────────────

    await db.commit()
    await db.refresh(purchase_request)
    return purchase_request


@router.delete("/{request_id}")
async def delete_purchase_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
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
