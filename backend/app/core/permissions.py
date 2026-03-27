from fastapi import Depends, HTTPException
from app.models import User
from app.api.v1.endpoints.auth import get_current_user


def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(403, "需要管理员权限")
    return current_user


# Permission definitions
ADMIN_PERMISSIONS = [
    "users:read",
    "users:create",
    "users:update",
    "users:delete",
    "assets:read",
    "assets:create",
    "assets:update",
    "assets:delete",
    "assets:import",
    "assets:export",
    "categories:read",
    "categories:create",
    "categories:update",
    "categories:delete",
    "suppliers:read",
    "suppliers:create",
    "suppliers:update",
    "suppliers:delete",
    "departments:read",
    "departments:create",
    "departments:update",
    "departments:delete",
    "purchase_requests:read",
    "purchase_requests:create",
    "purchase_requests:update",
    "purchase_requests:approve",
    "purchase_requests:reject",
    "approval_flows:read",
    "approval_flows:create",
    "approval_flows:update",
    "approval_flows:delete",
    "approval_instances:read",
    "approval_instances:approve",
    "approval_instances:reject",
    "audit_logs:read",
    "settings:read",
    "settings:update",
]

USER_PERMISSIONS = [
    "users:read:self",
    "assets:read",
    "categories:read",
    "suppliers:read",
    "departments:read",
    "purchase_requests:read:self",
    "purchase_requests:create",
    "approval_instances:read:my_pending",
]


def get_user_permissions(user: User) -> list[str]:
    """Get permission list for a user"""
    if user.is_superuser:
        return ADMIN_PERMISSIONS
    return USER_PERMISSIONS
