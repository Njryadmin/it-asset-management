from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import csv
import io
from datetime import datetime

from app.core.database import get_db
from app.models import Category
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.api.v1.endpoints.auth import get_current_active_user

router = APIRouter(prefix="/categories", tags=["分类管理"])


@router.get("")
async def list_categories(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    parent_id: Optional[int] = Query(None, description="父分类ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = select(Category)
    
    if keyword:
        query = query.where(Category.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Category.parent_id == parent_id)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {"total": total, "items": items}


@router.get("/tree")
async def get_category_tree(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取分类树形结构"""
    result = await db.execute(select(Category).where(Category.parent_id == None))
    root_categories = result.scalars().all()
    
    async def build_tree(category: Category) -> dict:
        children_result = await db.execute(
            select(Category).where(Category.parent_id == category.id)
        )
        children = children_result.scalars().all()
        return {
            "id": category.id,
            "name": category.name,
            "code": category.code,
            "parent_id": category.parent_id,
            "description": category.description,
            "created_at": category.created_at,
            "children": [await build_tree(child) for child in children]
        }
    
    tree = [await build_tree(cat) for cat in root_categories]
    return tree


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.post("")
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    # Check if code exists
    if category_in.code:
        result = await db.execute(select(Category).where(Category.code == category_in.code))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="分类代码已存在")
    
    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    if category_in.code:
        check_result = await db.execute(
            select(Category).where(Category.code == category_in.code, Category.id != category_id)
        )
        if check_result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="分类代码已存在")
    
    for key, value in category_in.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # Check if has children
    children_result = await db.execute(
        select(Category).where(Category.parent_id == category_id)
    )
    if children_result.scalars().first():
        raise HTTPException(status_code=400, detail="该分类包含子分类，无法删除")
    
    await db.delete(category)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/export")
async def export_categories(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """导出所有分类为CSV"""
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['分类名称', '编码', '上级分类ID', '描述', '创建时间'])
    
    for cat in categories:
        writer.writerow([
            cat.name,
            cat.code or '',
            cat.parent_id or '',
            cat.description or '',
            cat.created_at.strftime('%Y-%m-%d %H:%M:%S') if cat.created_at else ''
        ])
    
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.post("/import")
async def import_categories(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """批量导入分类(CSV格式)"""
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
            if not row.get('分类名称'):
                errors.append(f"第{row_num}行: 缺少必填字段(分类名称)")
                skipped += 1
                continue
            
            parent_id = None
            if row.get('上级分类ID'):
                parent_id = int(row['上级分类ID'])
            
            cat = Category(
                name=row['分类名称'],
                code=row.get('编码') or None,
                parent_id=parent_id,
                description=row.get('描述') or None
            )
            db.add(cat)
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
