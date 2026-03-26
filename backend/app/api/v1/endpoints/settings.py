from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import os
import uuid
import shutil

from app.core.database import get_db
from app.models import User, SystemSettings
from app.api.v1.endpoints.auth import get_current_active_user
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/settings", tags=["系统设置"])

# Static directory for uploads (configurable via environment)
STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")

# Default settings (used only when DB has no record)
DEFAULT_SETTINGS: Dict[str, Any] = {
    "system_name": "IT资产管理系统",
    "site_title": "IT资产管理系统",
    "site_description": "高效的IT资产管理系统",
    "company_name": "",
    "contact_email": "",
    "contact_phone": "",
    "asset_code_prefix": "ASSET",
    "auto_backup": True,
    "backup_retention_days": 30,
    "logo_url": "",
    "favicon_url": ""
}

# Theme presets
THEMES: Dict[str, Any] = {
    "default": {
        "name": "默认主题",
        "primary": "#1AAD19",
        "success": "#07C160",
        "warning": "#FF991A",
        "danger": "#FA5151",
        "info": "#909399",
        "bg_color": "#F5F5F5",
        "bg_color_secondary": "#E8E8E8",
        "sidebar_color": "rgba(255, 255, 255, 0.9)",
        "sidebar_text": "#333333",
        "sidebar_active_bg": "rgba(26, 173, 25, 0.12)",
        "header_color": "#ffffff",
        "header_text": "#333333",
        "card_bg": "#ffffff",
        "text_primary": "#333333",
        "text_secondary": "#666666",
        "text_placeholder": "#999999",
        "border_color": "#E5E5E5",
        "border_light": "#F0F0F0",
        "shadow": "0 2px 12px rgba(0,0,0,0.06)",
        "shadow_hover": "0 4px 16px rgba(0,0,0,0.1)",
    },
    "dark": {
        "name": "深色主题",
        "primary": "#07C160",
        "success": "#07C160",
        "warning": "#FF991A",
        "danger": "#FA5151",
        "info": "#909399",
        "bg_color": "#1F1F1F",
        "bg_color_secondary": "#2D2D2D",
        "sidebar_color": "#191919",
        "sidebar_text": "#E0E0E0",
        "sidebar_active_bg": "rgba(7,193,96,0.15)",
        "header_color": "#1F1F1F",
        "header_text": "#FFFFFF",
        "card_bg": "#252525",
        "text_primary": "#FFFFFF",
        "text_secondary": "#A0A0A0",
        "text_placeholder": "#6B6B6B",
        "border_color": "#3A3A3C",
        "border_light": "#2D2D2D",
        "shadow": "0 2px 8px rgba(0,0,0,0.3)",
        "shadow_hover": "0 4px 16px rgba(0,0,0,0.4)",
    },
}


async def get_or_create_settings(db: AsyncSession) -> SystemSettings:
    """Get existing settings or create default one"""
    result = await db.execute(select(SystemSettings))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SystemSettings(**DEFAULT_SETTINGS)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


def settings_to_dict(settings: SystemSettings) -> Dict[str, Any]:
    """Convert SystemSettings model to dict"""
    return {
        "system_name": settings.system_name,
        "site_title": settings.site_title,
        "site_description": settings.site_description,
        "company_name": settings.company_name,
        "contact_email": settings.contact_email,
        "contact_phone": settings.contact_phone,
        "asset_code_prefix": settings.asset_code_prefix,
        "auto_backup": settings.auto_backup,
        "backup_retention_days": settings.backup_retention_days,
        "logo_url": settings.logo_url,
        "favicon_url": settings.favicon_url,
    }


@router.get("")
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取系统设置"""
    settings = await get_or_create_settings(db)
    return settings_to_dict(settings)


@router.put("")
async def update_settings(
    new_settings: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新系统设置"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    settings = await get_or_create_settings(db)
    
    allowed_keys = {
        "system_name", "site_title", "site_description", "company_name", 
        "contact_email", "contact_phone", "asset_code_prefix", 
        "auto_backup", "backup_retention_days", "logo_url", "favicon_url"
    }
    
    for key, value in new_settings.items():
        if key in allowed_keys:
            setattr(settings, key, value)
    
    await db.commit()
    await db.refresh(settings)
    return {"message": "设置已更新", "settings": settings_to_dict(settings)}


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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取资产编号配置"""
    settings = await get_or_create_settings(db)
    prefix = settings.asset_code_prefix or "ASSET"
    return {
        "prefix": prefix,
        "example": f"{prefix}-2026-000001"
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


class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


@router.put("/profile")
async def update_user_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    if profile_data.full_name is not None:
        current_user.full_name = profile_data.full_name
    if profile_data.email is not None:
        # Check if email is taken by another user
        result = await db.execute(select(User).where(User.email == profile_data.email, User.id != current_user.id))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        current_user.email = profile_data.email
    
    await db.commit()
    await db.refresh(current_user)
    return {"message": "个人信息已更新"}


@router.put("/password")
async def change_current_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """修改当前用户密码"""
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    if len(password_data.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度至少6位")
    
    current_user.hashed_password = get_password_hash(password_data.new_password)
    await db.commit()
    return {"message": "密码修改成功"}


@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传站点LOGO"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/gif", "image/svg+xml", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 PNG/JPEG/GIF/SVG/WebP 格式")
    
    # Ensure static directory exists
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    filename = f"logo_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(STATIC_DIR, filename)
    
    # Save file
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Update settings in DB
    settings = await get_or_create_settings(db)
    settings.logo_url = f"/static/{filename}"
    await db.commit()
    
    return {"url": settings.logo_url}


@router.post("/upload-favicon")
async def upload_favicon(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传站点图标"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # Validate file type
    allowed_types = ["image/png", "image/x-icon", "image/vnd.microsoft.icon", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 PNG/ICO/SVG 格式")
    
    # Ensure static directory exists
    os.makedirs(STATIC_DIR, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if "." in file.filename else "ico"
    filename = f"favicon_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(STATIC_DIR, filename)
    
    # Save file
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Update settings in DB
    settings = await get_or_create_settings(db)
    settings.favicon_url = f"/static/{filename}"
    await db.commit()
    
    return {"url": settings.favicon_url}


@router.get("/static/{filename}")
async def get_static_file(filename: str):
    """获取静态文件"""
    # 防止路径遍历攻击
    filepath = os.path.normpath(os.path.join(STATIC_DIR, filename))
    if not filepath.startswith(os.path.abspath(STATIC_DIR)):
        raise HTTPException(status_code=400, detail="无效的文件路径")
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="文件不存在")
