from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any


async def log_action(
    db: AsyncSession,
    biz_type: str,
    biz_id: Optional[int],
    action: str,
    actor,
    before: Optional[Dict[str, Any]] = None,
    after: Optional[Dict[str, Any]] = None,
    asset_code: Optional[str] = None,
    summary: Optional[str] = None,
    actor_ip: Optional[str] = None,
):
    """
    Write an audit log entry.
    
    Args:
        db: Database session
        biz_type: Business type (assets/purchase_requests/categories/etc.)
        biz_id: Business record ID
        action: Action type (CREATE/UPDATE/DELETE/APPROVE/REJECT)
        actor: User object (or dict with id/name)
        before: State before the change
        after: State after the change
        asset_code: Asset code if applicable
        summary: Human-readable change summary
        actor_ip: Actor's IP address
    """
    actor_id = actor.id if hasattr(actor, 'id') else (actor.get('id') if isinstance(actor, dict) else None)
    actor_name = actor.full_name if hasattr(actor, 'full_name') else (actor.get('full_name') if isinstance(actor, dict) else None)

    audit_log = AuditLog(
        biz_type=biz_type,
        biz_id=biz_id,
        action=action,
        asset_code=asset_code,
        actor_id=actor_id,
        actor_name=actor_name,
        actor_ip=actor_ip,
        before_state=before,
        after_state=after,
        change_summary=summary,
    )
    db.add(audit_log)
    await db.commit()
    return audit_log
