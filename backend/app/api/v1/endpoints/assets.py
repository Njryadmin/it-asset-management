from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional
import csv
import io
from datetime import datetime

from app.core.database import get_db
from app.models import Asset, AssetStatus, Category, Supplier, Department, User
from app.schemas.schemas import AssetCreate, AssetUpdate, AssetResponse, AssetListResponse
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/assets", tags=["资产管理"])


@router.get("")
async def list_assets(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="资产状态"),
    department_id: Optional[int] = Query(None, description="部门ID"),
    region: Optional[str] = Query(None, description="地区"),
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
    if region:
        query = query.where(Asset.region.ilike(f"%{region}%"))
    
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


# IMPORTANT: /export and /import must be defined BEFORE /{asset_id}
# otherwise FastAPI will match them as {asset_id}

@router.get("/template")
async def download_asset_template(
    current_user=Depends(get_current_active_user)
):
    """下载资产导入模板"""
    output = io.StringIO()
    writer = csv.writer(output)
    # 模板使用名称，导入时自动查找对应ID
    writer.writerow([
        '资产编号', '名称', '序列号', '分类名称', '供应商名称', '部门名称',
        '使用人', '状态', '购入日期', '购入价格', '保修期至',
        '描述', '规格参数', '地区'
    ])
    writer.writerow([
        'ASSET-2026-000001', '示例资产', 'SN123456', '计算机设备', '联想官方旗舰店', '技术部',
        '', 'idle', '2026-01-01', '5000.00', '2027-01-01',
        '示例描述', '', '上海'
    ])
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=asset_template.csv"}
    )


@router.post("/import")
async def import_assets(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """批量导入资产(CSV格式)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")
    
    content = await file.read()
    decoded_content = content.decode('utf-8-sig')  # UTF-8 with BOM support
    
    reader = csv.DictReader(io.StringIO(decoded_content))
    
    imported = 0
    errors = []
    skipped = 0
    
    # 预先加载所有名称映射
    category_map = {c.name: c.id for c in (await db.execute(select(Category))).scalars().all()}
    supplier_map = {s.name: s.id for s in (await db.execute(select(Supplier))).scalars().all()}
    department_map = {d.name: d.id for d in (await db.execute(select(Department))).scalars().all()}
    # 用户名称映射
    user_name_map = {}
    for u in (await db.execute(select(User.username, User.full_name))).scalars().all():
        user_name_map[u.username] = u.id
        if u.full_name:
            user_name_map[u.full_name] = u.id
    
    for row_num, row in enumerate(reader, start=2):
        try:
            # Check required fields
            if not row.get('资产编号') or not row.get('名称'):
                errors.append(f"第{row_num}行: 缺少必填字段(资产编号/名称)")
                skipped += 1
                continue
            
            # Check if asset_code exists
            result = await db.execute(select(Asset).where(Asset.asset_code == row['资产编号']))
            if result.scalar_one_or_none():
                errors.append(f"第{row_num}行: 资产编号 {row['资产编号']} 已存在，跳过")
                skipped += 1
                continue
            
            # Parse category name -> id
            category_id = None
            if row.get('分类名称'):
                category_id = category_map.get(row['分类名称'])
                if not category_id:
                    errors.append(f"第{row_num}行: 分类 '{row['分类名称']}' 不存在")
                    skipped += 1
                    continue
            
            # Parse supplier name -> id
            supplier_id = None
            if row.get('供应商名称'):
                supplier_id = supplier_map.get(row['供应商名称'])
                # supplier_id can be None if not found, so just warning
                
            # Parse department name -> id  
            department_id = None
            if row.get('部门名称'):
                department_id = department_map.get(row['部门名称'])
                # department_id can be None if not found
            
            # Parse date fields
            purchase_date = None
            if row.get('购入日期'):
                try:
                    purchase_date = datetime.strptime(row['购入日期'], '%Y-%m-%d')
                except ValueError:
                    pass
            
            warranty_expire_date = None
            if row.get('保修期至'):
                try:
                    warranty_expire_date = datetime.strptime(row['保修期至'], '%Y-%m-%d')
                except ValueError:
                    pass
            
            status_str = row.get('状态', 'idle')
            try:
                status = AssetStatus(status_str)
            except ValueError:
                status = AssetStatus.idle
            
            asset = Asset(
                name=row['名称'],
                asset_code=row['资产编号'],
                serial_number=row.get('序列号') or None,
                category_id=category_id,
                supplier_id=supplier_id,
                department_id=department_id,
                assigned_to=user_name_map.get(row.get('使用人')) if row.get('使用人') else None,
                status=status,
                purchase_date=purchase_date,
                purchase_price=float(row['购入价格']) if row.get('购入价格') else None,
                warranty_expire_date=warranty_expire_date,
                description=row.get('描述') or None,
                specs=row.get('规格参数') or None,
                region=row.get('地区') or None,
            )
            db.add(asset)
            imported += 1
            
        except Exception as e:
            errors.append(f"第{row_num}行: {str(e)}")
            skipped += 1
    
    await db.commit()
    
    return {
        "message": f"导入完成",
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:20]  # Limit error messages
    }


@router.get("/export")
async def export_assets(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="资产状态"),
    department_id: Optional[int] = Query(None, description="部门ID"),
    region: Optional[str] = Query(None, description="地区"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """导出资产为CSV（支持筛选）"""
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
    if region:
        query = query.where(Asset.region.ilike(f"%{region}%"))
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header - 使用名称而非ID
    writer.writerow([
        '资产编号', '名称', '序列号', '分类名称', '供应商名称', '部门名称',
        '使用人', '状态', '购入日期', '购入价格', '保修期至',
        '描述', '规格参数', '地区'
    ])
    
    # 预先加载关联数据
    category_map = {c.id: c.name for c in (await db.execute(select(Category))).scalars().all()}
    supplier_map = {s.id: s.name for s in (await db.execute(select(Supplier))).scalars().all()}
    department_map = {d.id: d.name for d in (await db.execute(select(Department))).scalars().all()}
    # 加载用户名称
    user_result = await db.execute(select(User.id, User.username, User.full_name))
    user_map = {u.id: (u.full_name or u.username) for u in user_result.scalars().all()}
    
    # Data
    for asset in assets:
        assigned_user = user_map.get(asset.assigned_to, '') if asset.assigned_to else ''
        writer.writerow([
            asset.asset_code, asset.name, asset.serial_number,
            category_map.get(asset.category_id, ''),
            supplier_map.get(asset.supplier_id, ''),
            department_map.get(asset.department_id, ''),
            assigned_user, asset.status,
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
            asset.purchase_price, 
            asset.warranty_expire_date.strftime('%Y-%m-%d') if asset.warranty_expire_date else '',
            asset.description, asset.specs, asset.region or ''
        ])
    
    output.seek(0)
    # Add UTF-8 BOM for Excel compatibility
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.get("/{asset_id}")
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(
        select(Asset)
        .options(joinedload(Asset.assigned_to_user))
        .where(Asset.id == asset_id)
    )
    asset = result.unique().scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")

    # Build response dict and attach assigned_user_name
    resp = AssetResponse.model_validate(asset).model_dump()
    if asset.assigned_to_user:
        user = asset.assigned_to_user
        resp["assigned_user_name"] = user.full_name or user.username
    else:
        resp["assigned_user_name"] = None

    return resp


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


@router.post("/batch-delete")
async def batch_delete_assets(
    asset_ids: list[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量删除资产"""
    if len(asset_ids) > 100:
        raise HTTPException(status_code=400, detail="单次最多删除100条记录")
    
    result = await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
    assets = result.scalars().all()
    
    if len(assets) != len(asset_ids):
        found_ids = {a.id for a in assets}
        missing = set(asset_ids) - found_ids
        raise HTTPException(status_code=404, detail=f"部分资产不存在: {missing}")
    
    for asset in assets:
        await db.delete(asset)
    
    await db.commit()
    return {"message": f"成功删除 {len(assets)} 条资产"}


@router.post("/batch-transfer")
async def batch_transfer_assets(
    request: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """批量转移资产"""
    asset_ids: list[int] = request.get("asset_ids", [])
    to_department_id: int | None = request.get("to_department_id")
    to_user_id: int | None = request.get("to_user_id")
    reason: str | None = request.get("reason")
    
    if not asset_ids:
        raise HTTPException(status_code=400, detail="请选择要转移的资产")
    if len(asset_ids) > 100:
        raise HTTPException(status_code=400, detail="单次最多转移100条记录")
    if not to_department_id and not to_user_id:
        raise HTTPException(status_code=400, detail="请指定目标部门或目标使用人")
    
    # 获取资产
    result = await db.execute(select(Asset).where(Asset.id.in_(asset_ids)))
    assets = result.scalars().all()
    
    if len(assets) != len(asset_ids):
        raise HTTPException(status_code=404, detail="部分资产不存在")
    
    # 获取目标用户/部门信息
    from_user_ids = {a.assigned_to for a in assets if a.assigned_to}
    from_dept_ids = {a.department_id for a in assets if a.department_id}
    
    # 创建转移记录
    from app.models import AssetTransferLog, User, Department
    
    transfer_logs = []
    for asset in assets:
        log = AssetTransferLog(
            asset_id=asset.id,
            from_user_id=asset.assigned_to,
            to_user_id=to_user_id,
            from_department_id=asset.department_id,
            to_department_id=to_department_id,
            transfer_type="batch_transfer",
            reason=f"[批量转移] {reason}" if reason else "[批量转移]",
            operator_id=current_user.id
        )
        transfer_logs.append(log)
        
        # 更新资产
        if to_user_id is not None:
            asset.assigned_to = to_user_id
        if to_department_id is not None:
            asset.department_id = to_department_id
    
    db.add_all(transfer_logs)
    await db.commit()
    
    return {"message": f"成功转移 {len(assets)} 条资产", "count": len(assets)}
