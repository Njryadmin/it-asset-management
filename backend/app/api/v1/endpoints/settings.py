from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.core.database import get_db
from app.models import User
from app.api.v1.endpoints.auth import get_current_active_user

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
    
    # Only allow updating specific keys
    allowed_keys = {
        "system_name", "company_name", "contact_email", "contact_phone",
        "asset_code_prefix", "auto_backup", "backup_retention_days"
    }
    
    for key, value in settings.items():
        if key in allowed_keys:
            SETTINGS[key] = value
    
    return {"message": "设置已更新", "settings": SETTINGS}


@router.get("/asset-codes")
async def get_asset_code_config(
    current_user: User = Depends(get_current_active_user)
):
    """获取资产编号配置"""
    return {
        "prefix": SETTINGS.get("asset_code_prefix", "ASSET"),
        "example": f"{SETTINGS.get('asset_code_prefix', 'ASSET')}-2026-000001"
    }
