from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models import User
from app.models.audit_log import AuditLog
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/audit-logs", tags=["审计日志"])


# ============ Schemas ============
class AuditLogResponse(BaseModel):
    id: int
    biz_type: str
    biz_id: Optional[int]
    action: str
    asset_code: Optional[str]
    actor_id: Optional[int]
    actor_name: Optional[str]
    actor_ip: Optional[str]
    before_state: Optional[dict]
    after_state: Optional[dict]
    change_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    total: int
    items: List[AuditLogResponse]


# ============ Endpoints ============
@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    biz_type: Optional[str] = Query(None, description="业务类型"),
    action: Optional[str] = Query(None, description="操作类型"),
    actor_id: Optional[int] = Query(None, description="操作人ID"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取审计日志列表（分页、筛选）"""
    query = select(AuditLog)

    if biz_type:
        query = query.where(AuditLog.biz_type == biz_type)
    if action:
        query = query.where(AuditLog.action == action)
    if actor_id:
        query = query.where(AuditLog.actor_id == actor_id)
    if keyword:
        query = query.where(
            AuditLog.change_summary.ilike(f"%{keyword}%") |
            AuditLog.actor_name.ilike(f"%{keyword}%") |
            AuditLog.asset_code.ilike(f"%{keyword}%")
        )
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Order by created_at desc
    query = query.order_by(AuditLog.created_at.desc())
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "items": items}


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取审计日志详情"""
    result = await db.execute(select(AuditLog).where(AuditLog.id == audit_log_id))
    audit_log = result.scalar_one_or_none()
    if not audit_log:
        raise HTTPException(status_code=404, detail="审计日志不存在")
    return audit_log
