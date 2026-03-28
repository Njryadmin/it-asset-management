from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.core.permissions import require_admin, get_current_active_user
from app.models import User, Asset, AssetTransferLog
from app.schemas.schemas import (
    AssetTransferLogResponse,
    AssetTransferLogCreate,
    AssetTransferRequest
)

router = APIRouter(prefix="/asset-transfers", tags=["资产管理"])


@router.post("", response_model=AssetTransferLogResponse)
async def create_transfer_log(
    transfer: AssetTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建资产转移/分配记录"""
    # 获取资产信息
    result = await db.execute(select(Asset).where(Asset.id == transfer.asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    # 创建转移记录
    log = AssetTransferLog(
        asset_id=transfer.asset_id,
        from_user_id=asset.assigned_to,
        to_user_id=transfer.to_user_id,
        from_department_id=asset.department_id,
        to_department_id=transfer.to_department_id,
        transfer_type="transfer" if transfer.to_user_id else "assign",
        reason=transfer.reason,
        operator_id=current_user.id
    )
    
    # 更新资产的使用人和部门
    if transfer.to_user_id is not None:
        asset.assigned_to = transfer.to_user_id
    if transfer.to_department_id is not None:
        asset.department_id = transfer.to_department_id
    asset.updated_at = datetime.utcnow()

    db.add(log)
    await db.commit()
    await db.refresh(log)

    # 返回完整信息
    response = AssetTransferLogResponse(
        id=log.id,
        asset_id=log.asset_id,
        from_user_id=log.from_user_id,
        to_user_id=log.to_user_id,
        from_department_id=log.from_department_id,
        to_department_id=log.to_department_id,
        transfer_type=log.transfer_type,
        reason=log.reason,
        operator_id=log.operator_id,
        created_at=log.created_at,
        asset_name=asset.name if asset else None,
        from_user_name=None,
        to_user_name=None,
        from_department_name=None,
        to_department_name=None,
        operator_name=current_user.full_name or current_user.username
    )
    return response


@router.get("/asset/{asset_id}", response_model=list[AssetTransferLogResponse])
async def get_asset_transfer_history(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取资产的转移历史"""
    result = await db.execute(
        select(AssetTransferLog)
        .where(AssetTransferLog.asset_id == asset_id)
        .order_by(desc(AssetTransferLog.created_at))
    )
    logs = result.scalars().all()

    # 获取用户和部门名称
    user_ids = set()
    dept_ids = set()
    for log in logs:
        if log.from_user_id:
            user_ids.add(log.from_user_id)
        if log.to_user_id:
            user_ids.add(log.to_user_id)
        if log.from_department_id:
            dept_ids.add(log.from_department_id)
        if log.to_department_id:
            dept_ids.add(log.to_department_id)
        user_ids.add(log.operator_id)

    # 批量查询
    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u for u in users_result.scalars().all()}

    from app.models import Department
    if dept_ids:
        depts_result = await db.execute(select(Department).where(Department.id.in_(dept_ids)))
        depts = {d.id: d for d in depts_result.scalars().all()}
    else:
        depts = {}

    # 获取资产名称
    asset_result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = asset_result.scalar_one_or_none()

    return [
        AssetTransferLogResponse(
            id=log.id,
            asset_id=log.asset_id,
            from_user_id=log.from_user_id,
            to_user_id=log.to_user_id,
            from_department_id=log.from_department_id,
            to_department_id=log.to_department_id,
            transfer_type=log.transfer_type,
            reason=log.reason,
            operator_id=log.operator_id,
            created_at=log.created_at,
            asset_name=asset.name if asset else None,
            from_user_name=users.get(log.from_user_id).full_name if log.from_user_id and log.from_user_id in users else None,
            to_user_name=users.get(log.to_user_id).full_name if log.to_user_id and log.to_user_id in users else None,
            from_department_name=depts.get(log.from_department_id).name if log.from_department_id and log.from_department_id in depts else None,
            to_department_name=depts.get(log.to_department_id).name if log.to_department_id and log.to_department_id in depts else None,
            operator_name=users.get(log.operator_id).full_name if log.operator_id in users else None
        )
        for log in logs
    ]


@router.get("", response_model=list[AssetTransferLogResponse])
async def list_transfer_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取转移记录列表"""
    query = select(AssetTransferLog).order_by(desc(AssetTransferLog.created_at))
    
    if keyword:
        query = query.where(AssetTransferLog.reason.contains(keyword))
    
    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    result = await db.execute(query)
    logs = result.scalars().all()

    # 获取关联信息
    asset_ids = [log.asset_id for log in logs]
    user_ids = set()
    dept_ids = set()
    for log in logs:
        if log.from_user_id:
            user_ids.add(log.from_user_id)
        if log.to_user_id:
            user_ids.add(log.to_user_id)
        user_ids.add(log.operator_id)
        if log.from_department_id:
            dept_ids.add(log.from_department_id)
        if log.to_department_id:
            dept_ids.add(log.to_department_id)

    users_result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = {u.id: u for u in users_result.scalars().all()}

    from app.models import Department
    if dept_ids:
        depts_result = await db.execute(select(Department).where(Department.id.in_(dept_ids)))
        depts = {d.id: d for d in depts_result.scalars().all()}
    else:
        depts = {}

    assets_result = await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
    assets = {a.id: a for a in assets_result.scalars().all()}

    return [
        AssetTransferLogResponse(
            id=log.id,
            asset_id=log.asset_id,
            from_user_id=log.from_user_id,
            to_user_id=log.to_user_id,
            from_department_id=log.from_department_id,
            to_department_id=log.to_department_id,
            transfer_type=log.transfer_type,
            reason=log.reason,
            operator_id=log.operator_id,
            created_at=log.created_at,
            asset_name=assets.get(log.asset_id).name if log.asset_id in assets else None,
            from_user_name=users.get(log.from_user_id).full_name if log.from_user_id and log.from_user_id in users else None,
            to_user_name=users.get(log.to_user_id).full_name if log.to_user_id and log.to_user_id in users else None,
            from_department_name=depts.get(log.from_department_id).name if log.from_department_id and log.from_department_id in depts else None,
            to_department_name=depts.get(log.to_department_id).name if log.to_department_id and log.to_department_id in depts else None,
            operator_name=users.get(log.operator_id).full_name if log.operator_id in users else None
        )
        for log in logs
    ]
