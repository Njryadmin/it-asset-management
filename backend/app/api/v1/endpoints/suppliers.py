from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import csv
import io
from datetime import datetime

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


# IMPORTANT: /export and /import must be defined BEFORE /{supplier_id}
# otherwise FastAPI will match them as {supplier_id}

@router.get("/export")
async def export_suppliers(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """导出所有供应商为CSV"""
    result = await db.execute(select(Supplier))
    suppliers = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['供应商名称', '编码', '联系人', '电话', '邮箱', '地址', '描述', '状态', '创建时间'])
    
    for sup in suppliers:
        writer.writerow([
            sup.name,
            sup.code or '',
            sup.contact_person or '',
            sup.phone or '',
            sup.email or '',
            sup.address or '',
            sup.description or '',
            '启用' if sup.is_active else '禁用',
            sup.created_at.strftime('%Y-%m-%d %H:%M:%S') if sup.created_at else ''
        ])
    
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=suppliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.get("/template")
async def download_supplier_template(
    current_user=Depends(get_current_active_user)
):
    """下载供应商导入模板"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['供应商名称', '编码', '联系人', '电话', '邮箱', '地址', '描述', '状态'])
    writer.writerow(['示例供应商', 'SUP001', '张三', '13800138000', 'example@example.com', '示例地址', '示例描述', '启用'])
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=supplier_template.csv"}
    )


@router.post("/{supplier_id}/toggle-status")
async def toggle_supplier_status(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """切换供应商启用/禁用状态"""
    result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    supplier.is_active = not supplier.is_active
    await db.commit()
    await db.refresh(supplier)
    return {"message": "状态切换成功", "is_active": supplier.is_active}


@router.post("/import")
async def import_suppliers(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """批量导入供应商(CSV格式)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")
    
    content = await file.read()
    decoded_content = content.decode('utf-8-sig')
    
    reader = csv.DictReader(io.StringIO(decoded_content))
    
    imported = 0
    errors = []
    skipped = 0
    
    for row_num, row in enumerate(reader, start=2):
        try:
            if not row.get('供应商名称'):
                errors.append(f"第{row_num}行: 缺少必填字段(供应商名称)")
                skipped += 1
                continue
            
            # Check if code exists
            code = row.get('编码', '').strip() or None
            if code:
                result = await db.execute(select(Supplier).where(Supplier.code == code))
                if result.scalar_one_or_none():
                    errors.append(f"第{row_num}行: 编码 {code} 已存在，跳过")
                    skipped += 1
                    continue
            
            status_val = row.get('状态', '').strip()
            is_active = status_val != '禁用'
            
            sup = Supplier(
                name=row['供应商名称'],
                code=code,
                contact_person=row.get('联系人', '').strip() or None,
                phone=row.get('电话', '').strip() or None,
                email=row.get('邮箱', '').strip() or None,
                address=row.get('地址', '').strip() or None,
                description=row.get('描述', '').strip() or None,
                is_active=is_active
            )
            db.add(sup)
            imported += 1
            
        except Exception as e:
            errors.append(f"第{row_num}行: {str(e)}")
            skipped += 1
    
    await db.commit()
    
    return {
        "message": f"导入完成",
        "imported": imported,
        "skipped": skipped,
        "errors": errors[:20]
    }


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
