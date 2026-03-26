from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.core.database import get_db
from app.models import User
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/settings", tags=["系统设置"])


# In-memory settings (in production, use database)
SETTINGS: Dict[str, Any] = {
    "system_name": "IT资产管理系统",
    "company_name": "",
    "contact_email": "",
    "contact_phone": "",
    "asset_code_prefix": "ASSET",
    "auto_backup": True,
    "backup_retention_days": 30
}

# Theme presets
THEMES: Dict[str, Any] = {
    "default": {
        "name": "默认主题",
        "primary": "#409eff",
        "bg_color": "#f5f7fa",
        "sidebar_color": "#304156",
        "header_color": "#ffffff"
    },
    "dark": {
        "name": "深色主题",
        "primary": "#409eff",
        "bg_color": "#1a1a2e",
        "sidebar_color": "#16213e",
        "header_color": "#16213e"
    },
    "green": {
        "name": "绿色主题",
        "primary": "#67c23a",
        "bg_color": "#f0f9eb",
        "sidebar_color": "#1a5c1a",
        "header_color": "#ffffff"
    },
    "purple": {
        "name": "紫色主题",
        "primary": "#a371f7",
        "bg_color": "#f5f3ff",
        "sidebar_color": "#2d1b4e",
        "header_color": "#ffffff"
    }
}


@router.get("")
async def get_settings(
    current_user: User = Depends(get_current_active_user)
):
    """获取系统设置"""
    return SETTINGS


@router.put("")
async def update_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """更新系统设置"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    allowed_keys = {
        "system_name", "company_name", "contact_email", "contact_phone",
        "asset_code_prefix", "auto_backup", "backup_retention_days"
    }
    
    for key, value in settings.items():
        if key in allowed_keys:
            SETTINGS[key] = value
    
    return {"message": "设置已更新", "settings": SETTINGS}


@router.get("/themes")
async def get_themes(
    current_user: User = Depends(get_current_active_user)
):
    """获取主题列表"""
    return THEMES


@router.get("/theme")
async def get_current_theme(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前主题"""
    return THEMES.get("default")


@router.get("/asset-codes")
async def get_asset_code_config(
    current_user: User = Depends(get_current_active_user)
):
    """获取资产编号配置"""
    return {
        "prefix": SETTINGS.get("asset_code_prefix", "ASSET"),
        "example": f"{SETTINGS.get('asset_code_prefix', 'ASSET')}-2026-000001"
    }


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_superuser": current_user.is_superuser
    }


@router.put("/profile")
async def update_user_profile(
    full_name: str = None,
    email: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    if full_name is not None:
        current_user.full_name = full_name
    if email is not None:
        # Check if email is taken by another user
        result = await db.execute(select(User).where(User.email == email, User.id != current_user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        current_user.email = email
    
    await db.commit()
    await db.refresh(current_user)
    return {"message": "个人信息已更新"}


@router.put("/password")
async def change_current_password(
    old_password: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """修改当前用户密码"""
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少6位")
    
    current_user.password_hash = get_password_hash(new_password)
    await db.commit()
    return {"message": "密码修改成功"}
