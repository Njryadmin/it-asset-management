from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.models import Department
from app.schemas.schemas import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.api.v1.endpoints.auth import get_current_active_user

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
    current_user=Depends(get_current_active_user)
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
    current_user=Depends(get_current_active_user)
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
    current_user=Depends(get_current_active_user)
):
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    if not department:
        raise HTTPException(status_code=404, detail="部门不存在")
    
    await db.delete(department)
    await db.commit()
    return {"message": "删除成功"}
