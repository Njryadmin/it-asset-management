from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class ApprovalFlow(Base):
    __tablename__ = "approval_flows"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)  # "采购审批流"
    flow_code = Column(String(50), nullable=False, unique=True)
    applicable_to = Column(String(50), nullable=False)  # purchase_request
    steps = Column(JSONB, nullable=False)  # [{"step":1,"role":"admin","threshold":0}]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
