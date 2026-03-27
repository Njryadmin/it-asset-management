from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models import User
from app.models.approval_flow import ApprovalFlow
from app.models.approval_instance import ApprovalInstance
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/approval-instances", tags=["审批管理"])


# ============ Schemas ============
class ApprovalFlowBase(BaseModel):
    name: str
    flow_code: str
    applicable_to: str
    steps: list
    is_active: bool = True


class ApprovalFlowCreate(ApprovalFlowBase):
    pass


class ApprovalFlowUpdate(BaseModel):
    name: Optional[str] = None
    steps: Optional[list] = None
    is_active: Optional[bool] = None


class ApprovalFlowResponse(ApprovalFlowBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalFlowListResponse(BaseModel):
    total: int
    items: List[ApprovalFlowResponse]


class ApprovalChainItem(BaseModel):
    step: int
    approver: Optional[str] = None
    approver_id: Optional[int] = None
    action: str
    comment: Optional[str] = None
    time: Optional[str] = None


class ApprovalInstanceResponse(BaseModel):
    id: int
    flow_id: Optional[int]
    instance_no: str
    biz_type: str
    biz_id: int
    applicant_id: Optional[int]
    applicant_name: Optional[str]
    current_step: int
    status: str
    approval_chain: List[dict]
    total_steps: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalInstanceListResponse(BaseModel):
    total: int
    items: List[ApprovalInstanceResponse]


class ApprovalActionRequest(BaseModel):
    comment: Optional[str] = None


# ============ Approval Flows ============
approval_flows_router = APIRouter(prefix="/approval-flows", tags=["审批流程"])


@approval_flows_router.get("", response_model=ApprovalFlowListResponse)
async def list_approval_flows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取审批流程模板列表"""
    query = select(ApprovalFlow).where(ApprovalFlow.is_active == True)
    result = await db.execute(query)
    items = result.scalars().all()
    return {"total": len(items), "items": items}


@approval_flows_router.post("", response_model=ApprovalFlowResponse)
async def create_approval_flow(
    flow_in: ApprovalFlowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建审批流程模板（管理员）"""
    # Check if flow_code exists
    result = await db.execute(select(ApprovalFlow).where(ApprovalFlow.flow_code == flow_in.flow_code))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="流程代码已存在")

    flow = ApprovalFlow(**flow_in.model_dump())
    db.add(flow)
    await db.commit()
    await db.refresh(flow)
    return flow


@approval_flows_router.put("/{flow_id}", response_model=ApprovalFlowResponse)
async def update_approval_flow(
    flow_id: int,
    flow_in: ApprovalFlowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新审批流程模板（管理员）"""
    result = await db.execute(select(ApprovalFlow).where(ApprovalFlow.id == flow_id))
    flow = result.scalar_one_or_none()
    if not flow:
        raise HTTPException(status_code=404, detail="审批流程不存在")

    update_data = flow_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(flow, key, value)

    await db.commit()
    await db.refresh(flow)
    return flow


# ============ Approval Instances ============

@router.get("", response_model=ApprovalInstanceListResponse)
async def list_approval_instances(
    status: Optional[str] = Query(None, description="状态"),
    biz_type: Optional[str] = Query(None, description="业务类型"),
    applicant_id: Optional[int] = Query(None, description="申请人ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取审批实例列表"""
    query = select(ApprovalInstance)

    if status:
        query = query.where(ApprovalInstance.status == status)
    if biz_type:
        query = query.where(ApprovalInstance.biz_type == biz_type)
    if applicant_id:
        query = query.where(ApprovalInstance.applicant_id == applicant_id)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(ApprovalInstance.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "items": items}


@router.get("/my-pending", response_model=ApprovalInstanceListResponse)
async def list_my_pending_approvals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户待审批的实例"""
    query = select(ApprovalInstance).where(
        ApprovalInstance.status == "pending"
    ).order_by(ApprovalInstance.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()
    return {"total": len(items), "items": items}


@router.get("/{instance_id}", response_model=ApprovalInstanceResponse)
async def get_approval_instance(
    instance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取审批实例详情"""
    result = await db.execute(select(ApprovalInstance).where(ApprovalInstance.id == instance_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="审批实例不存在")
    return instance


@router.post("/{instance_id}/approve")
async def approve_approval_instance(
    instance_id: int,
    action_data: ApprovalActionRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """审批通过"""
    result = await db.execute(select(ApprovalInstance).where(ApprovalInstance.id == instance_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="审批实例不存在")

    if instance.status != "pending":
        raise HTTPException(status_code=400, detail="只能审批待处理状态的申请")

    # Get flow to check steps
    flow_result = await db.execute(select(ApprovalFlow).where(ApprovalFlow.id == instance.flow_id))
    flow = flow_result.scalar_one_or_none()

    # Record approval
    approval_record = {
        "step": instance.current_step,
        "approver": current_user.full_name or current_user.username,
        "approver_id": current_user.id,
        "action": "approve",
        "comment": action_data.comment if action_data else None,
        "time": datetime.utcnow().isoformat(),
    }

    # Append to approval chain
    chain = list(instance.approval_chain or [])
    chain.append(approval_record)
    instance.approval_chain = chain

    # Check if all steps completed
    if instance.total_steps and instance.current_step >= instance.total_steps:
        instance.status = "approved"
    else:
        # Advance to next step
        instance.current_step += 1

    await db.commit()
    await db.refresh(instance)
    return instance


@router.post("/{instance_id}/reject")
async def reject_approval_instance(
    instance_id: int,
    action_data: ApprovalActionRequest = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """审批拒绝"""
    result = await db.execute(select(ApprovalInstance).where(ApprovalInstance.id == instance_id))
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="审批实例不存在")

    if instance.status != "pending":
        raise HTTPException(status_code=400, detail="只能拒绝待处理状态的申请")

    # Record rejection
    approval_record = {
        "step": instance.current_step,
        "approver": current_user.full_name or current_user.username,
        "approver_id": current_user.id,
        "action": "reject",
        "comment": action_data.comment if action_data else None,
        "time": datetime.utcnow().isoformat(),
    }

    chain = list(instance.approval_chain or [])
    chain.append(approval_record)
    instance.approval_chain = chain
    instance.status = "rejected"

    await db.commit()
    await db.refresh(instance)
    return instance
