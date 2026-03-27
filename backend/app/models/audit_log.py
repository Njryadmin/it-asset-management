from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True)
    biz_type = Column(String(50), nullable=False)  # assets/purchase_requests/categories...
    biz_id = Column(BigInteger, nullable=True)
    action = Column(String(50), nullable=False)  # CREATE/UPDATE/DELETE/APPROVE/REJECT
    asset_code = Column(String(100), nullable=True)
    actor_id = Column(BigInteger, nullable=True)
    actor_name = Column(String(200), nullable=True)
    actor_ip = Column(String(50), nullable=True)
    before_state = Column(JSONB, nullable=True)
    after_state = Column(JSONB, nullable=True)
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
