from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import csv
import io
from datetime import datetime

from app.core.database import get_db
from app.models import Department, User, Asset
from app.schemas.schemas import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.permissions import require_admin

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.get("")
async def list_departments(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    parent_id: Optional[int] = Query(None, description="父部门ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    query = select(Department)
    
    if keyword:
        query = query.where(Department.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Department.parent_id == parent_id)
    
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
async def get_department_tree(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """获取部门树形结构"""
    result = await db.execute(select(Department).where(Department.parent_id == None))
    root_departments = result.scalars().all()
    
    async def build_tree(dept: Department) -> dict:
        children_result = await db.execute(
            select(Department).where(Department.parent_id == dept.id)
        )
        children = children_result.scalars().all()
        return {
            "id": dept.id,
            "name": dept.name,
            "code": dept.code,
            "parent_id": dept.parent_id,
            "description": dept.description,
            "created_at": dept.created_at,
            "children": [await build_tree(child) for child in children]
        }
    
    tree = [await build_tree(dept) for dept in root_departments]
    return tree


@router.get("/export")
async def export_departments(
    fields: Optional[str] = Query(None, description="导出字段，逗号分隔，如'name,code,description'"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    """导出部门为CSV（支持按字段导出）"""
    result = await db.execute(select(Department))
    departments = result.scalars().all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 字段配置：key -> (中文表头, 取值函数)
    FIELD_CONFIG = {
        'name': ('部门名称', lambda d: d.name),
        'code': ('编码', lambda d: d.code or ''),
        'parent': ('上级部门名称', None),  # 特殊处理
        'description': ('描述', lambda d: d.description or ''),
        'created_at': ('创建时间', lambda d: d.created_at.strftime('%Y-%m-%d %H:%M:%S') if d.created_at else ''),
    }
    
    # 支持的字段列表（按顺序）
    ALL_FIELDS = ['name', 'code', 'parent', 'description', 'created_at']
    
    # 确定要导出的字段
    if fields:
        selected = [f.strip() for f in fields.split(',') if f.strip() in FIELD_CONFIG]
    else:
        selected = ALL_FIELDS
    
    # Build parent name lookup（从所有部门中构建，确保能找到）
    all_depts_result = await db.execute(select(Department.id, Department.name))
    dept_id_to_name = {row[0]: row[1] for row in all_depts_result.all()}
    
    # 写入表头
    headers = [FIELD_CONFIG[f][0] for f in selected]
    writer.writerow(headers)
    
    # 写入数据
    for dept in departments:
        row = []
        for f in selected:
            if f == 'parent':
                parent_name = dept_id_to_name.get(dept.parent_id, '') if dept.parent_id else ''
                row.append(parent_name)
            else:
                row.append(FIELD_CONFIG[f][1](dept))
        writer.writerow(row)
    
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=departments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@router.get("/{department_id}")
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="部门不存在")
    return department


@router.post("")
async def create_department(
    department_in: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    if department_in.code:
        result = await db.execute(select(Department).where(Department.code == department_in.code))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="部门代码已存在")
    
    department = Department(**department_in.model_dump())
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


@router.put("/{department_id}")
async def update_department(
    department_id: int,
    department_in: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    for key, value in department_in.model_dump(exclude_unset=True).items():
        setattr(department, key, value)
    
    await db.commit()
    await db.refresh(department)
    return department


@router.delete("/{department_id}")
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    # Check if has children
    children_result = await db.execute(
        select(Department).where(Department.parent_id == department_id)
    )
    if children_result.scalars().first():
        raise HTTPException(status_code=400, detail="该部门包含子部门，无法删除")
    
    # Check if has users
    users_result = await db.execute(
        select(User).where(User.department_id == department_id)
    )
    if users_result.scalars().first():
        raise HTTPException(status_code=400, detail="该部门下有用户，无法删除")
    
    # Check if has assets
    assets_result = await db.execute(
        select(Asset).where(Asset.department_id == department_id)
    )
    if assets_result.scalars().first():
        raise HTTPException(status_code=400, detail="该部门下有资产，无法删除")
    
    await db.delete(department)
    await db.commit()
    return {"message": "删除成功"}


@router.get("/template")
async def download_department_template(
    current_user=Depends(get_current_active_user)
):
    """下载部门导入模板"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['部门名称', '编码', '上级部门名称', '描述'])
    writer.writerow(['示例部门', 'DEPT01', '', '示例描述（上级部门名称留空表示顶级部门）'])
    output.seek(0)
    bom = '\ufeff'
    return StreamingResponse(
        iter([bom + output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=department_template.csv"}
    )


@router.post("/import")
async def import_departments(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_admin)
):
    """批量导入部门(CSV格式)"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="仅支持CSV文件")
    
    content = await file.read()
    decoded_content = content.decode('utf-8-sig')
    
    reader = csv.DictReader(io.StringIO(decoded_content))
    
    # 预先查询所有现有部门
    existing_result = await db.execute(select(Department))
    existing_departments = existing_result.scalars().all()
    existing_ids = {dept.id for dept in existing_departments}
    existing_codes = {dept.code for dept in existing_departments if dept.code}
    name_to_id = {dept.name: dept.id for dept in existing_departments}
    
    imported = 0
    errors = []
    skipped = 0
    
    for row_num, row in enumerate(reader, start=2):
        try:
            if not row.get('部门名称'):
                errors.append(f"第{row_num}行: 缺少必填字段(部门名称)")
                skipped += 1
                continue
            
            # Check if code exists
            if row.get('编码'):
                if row['编码'] in existing_codes:
                    errors.append(f"第{row_num}行: 编码 {row['编码']} 已存在，跳过")
                    skipped += 1
                    continue
            
            parent_id = None
            parent_name = row.get('上级部门名称', '').strip()
            if parent_name:
                parent_id = name_to_id.get(parent_name)
                if parent_id is None:
                    errors.append(f"第{row_num}行: 未找到上级部门'{parent_name}'，跳过")
                    skipped += 1
                    continue
            
            dept = Department(
                name=row['部门名称'],
                code=row.get('编码') or None,
                parent_id=parent_id,
                description=row.get('描述') or None
            )
            db.add(dept)
            # Update name lookup for chain references within this import
            name_to_id[dept.name] = dept.id
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
