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
        "success": "#67c23a",
        "warning": "#e6a23c",
        "danger": "#f56c6c",
        "info": "#909399",
        "bg_color": "#f0f2f5",
        "sidebar_color": "#304156",
        "sidebar_text": "#bfcbd9",
        "sidebar_active_bg": "#263445",
        "header_color": "#ffffff",
        "header_text": "#303133",
        "card_bg": "#ffffff",
        "text_primary": "#303133",
        "text_secondary": "#606266",
        "text_placeholder": "#c0c4cc",
        "border_color": "#e4e7ed",
        "border_light": "#f0f2f5",
        "shadow": "0 2px 12px rgba(0,0,0,0.08)",
        "shadow_hover": "0 4px 20px rgba(0,0,0,0.12)",
    },
    "dark": {
        "name": "深色主题",
        "primary": "#409eff",
        "success": "#67c23a",
        "warning": "#e6a23c",
        "danger": "#f56c6c",
        "info": "#909399",
        "bg_color": "#0d1117",
        "sidebar_color": "#161b22",
        "sidebar_text": "#8b949e",
        "sidebar_active_bg": "#1f6feb33",
        "header_color": "#161b22",
        "header_text": "#c9d1d9",
        "card_bg": "#161b22",
        "text_primary": "#c9d1d9",
        "text_secondary": "#8b949e",
        "text_placeholder": "#484f58",
        "border_color": "#30363d",
        "border_light": "#21262d",
        "shadow": "0 2px 12px rgba(0,0,0,0.4)",
        "shadow_hover": "0 4px 20px rgba(0,0,0,0.5)",
    },
    "green": {
        "name": "绿色主题",
        "primary": "#2eb872",
        "success": "#52b77a",
        "warning": "#f5a623",
        "danger": "#e5534b",
        "info": "#8bc34a",
        "bg_color": "#f0f9eb",
        "sidebar_color": "#1a5c1a",
        "sidebar_text": "#a6e7b0",
        "sidebar_active_bg": "#2eb87222",
        "header_color": "#ffffff",
        "header_text": "#303133",
        "card_bg": "#ffffff",
        "text_primary": "#303133",
        "text_secondary": "#606266",
        "text_placeholder": "#c0c4cc",
        "border_color": "#e1f3d8",
        "border_light": "#f0f9eb",
        "shadow": "0 2px 12px rgba(46,184,114,0.12)",
        "shadow_hover": "0 4px 20px rgba(46,184,114,0.2)",
    },
    "purple": {
        "name": "紫色主题",
        "primary": "#a371f7",
        "success": "#67c23a",
        "warning": "#e6a23c",
        "danger": "#f56c6c",
        "info": "#909399",
        "bg_color": "#f5f3ff",
        "sidebar_color": "#2d1b4e",
        "sidebar_text": "#d2b4fa",
        "sidebar_active_bg": "#a371f722",
        "header_color": "#ffffff",
        "header_text": "#303133",
        "card_bg": "#ffffff",
        "text_primary": "#303133",
        "text_secondary": "#606266",
        "text_placeholder": "#c0c4cc",
        "border_color": "#ede9fe",
        "border_light": "#f5f3ff",
        "shadow": "0 2px 12px rgba(163,113,247,0.12)",
        "shadow_hover": "0 4px 20px rgba(163,113,247,0.2)",
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
