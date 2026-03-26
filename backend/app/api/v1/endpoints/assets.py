from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
import csv
import io
from datetime import datetime

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


# IMPORTANT: /export and /import must be defined BEFORE /{asset_id}
# otherwise FastAPI will match them as {asset_id}

@router.get("/export")
async def export_assets(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """导出所有资产为CSV"""
    result = await db.execute(select(Asset))
    assets = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        '资产编号', '名称', '序列号', '分类ID', '供应商ID', '部门ID',
        '使用人ID', '状态', '购入日期', '购入价格', '保修期至',
        '描述', '规格参数', '创建时间', '更新时间'
    ])
    
    # Data
    for asset in assets:
        writer.writerow([
            asset.asset_code, asset.name, asset.serial_number,
            asset.category_id, asset.supplier_id, asset.department_id,
            asset.assigned_to, asset.status,
            asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
            asset.purchase_price, 
            asset.warranty_expire_date.strftime('%Y-%m-%d') if asset.warranty_expire_date else '',
            asset.description, asset.specs,
            asset.created_at.strftime('%Y-%m-%d %H:%M:%S') if asset.created_at else '',
            asset.updated_at.strftime('%Y-%m-%d %H:%M:%S') if asset.updated_at else ''
        ])
    
    output.seek(0)
    # Add UTF-8 BOM for Excel compatibility
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
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
    
    for row_num, row in enumerate(reader, start=2):
        try:
            # Check required fields
            if not row.get('资产编号') or not row.get('名称') or not row.get('分类ID'):
                errors.append(f"第{row_num}行: 缺少必填字段(资产编号/名称/分类ID)")
                skipped += 1
                continue
            
            # Check if asset_code exists
            result = await db.execute(select(Asset).where(Asset.asset_code == row['资产编号']))
            if result.scalar_one_or_none():
                errors.append(f"第{row_num}行: 资产编号 {row['资产编号']} 已存在，跳过")
                skipped += 1
                continue
            
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
            
            asset = Asset(
                name=row['名称'],
                asset_code=row['资产编号'],
                serial_number=row.get('序列号') or None,
                category_id=int(row['分类ID']),
                supplier_id=int(row['供应商ID']) if row.get('供应商ID') else None,
                department_id=int(row['部门ID']) if row.get('部门ID') else None,
                assigned_to=int(row['使用人ID']) if row.get('使用人ID') else None,
                status=row.get('状态', 'idle'),
                purchase_date=purchase_date,
                purchase_price=float(row['购入价格']) if row.get('购入价格') else None,
                warranty_expire_date=warranty_expire_date,
                description=row.get('描述') or None,
                specs=row.get('规格参数') or None,
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
