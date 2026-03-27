from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.core.database import get_db
from app.models import User
from app.schemas.schemas import UserResponse, UserCreate, UserUpdate, UserListResponse
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.security import get_password_hash, verify_password
from app.core.permissions import require_admin, get_user_permissions

router = APIRouter(prefix="/users", tags=["用户管理"])


class UserPermissionsResponse(BaseModel):
    permissions: List[str]


class PasswordChangeRequest(BaseModel):
    old_password: Optional[str] = None
    new_password: str


@router.get("/me/permissions", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_active_user),
):
    """获取当前用户权限列表"""
    permissions = get_user_permissions(current_user)
    return {"permissions": permissions}


@router.get("", response_model=UserListResponse)
async def list_users(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取用户列表（管理员）"""
    query = select(User)

    if keyword:
        query = query.where(
            User.username.ilike(f"%{keyword}%") |
            User.email.ilike(f"%{keyword}%") |
            User.full_name.ilike(f"%{keyword}%")
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"total": total, "items": items}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取用户详情（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建用户（管理员）"""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    # Check if email exists
    if user_in.email:
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")

    user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_superuser=getattr(user_in, 'is_superuser', False),
        is_active=getattr(user_in, 'is_active', True)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新用户（管理员）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Check if email exists (excluding current user)
    if user_in.email and user_in.email != user.email:
        result = await db.execute(select(User).where(User.email == user_in.email, User.id != user_id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")

    update_data = user_in.model_dump(exclude_unset=True)

    # Handle password separately
    if 'password' in update_data:
        user.hashed_password = get_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除用户（管理员）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}


@router.put("/{user_id}/password")
async def change_password(
    user_id: int,
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """修改密码"""
    # Users can only change their own password, admins can change any
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="权限不足")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # Non-admin users must provide correct old password
    if not current_user.is_superuser:
        if not verify_password(password_data.old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="原密码错误")

    # Password strength validation
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少6位")

    user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    return {"message": "密码修改成功"}
