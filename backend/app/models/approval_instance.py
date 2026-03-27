from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class ApprovalInstance(Base):
    __tablename__ = "approval_instances"

    id = Column(BigInteger, primary_key=True)
    flow_id = Column(BigInteger, ForeignKey("approval_flows.id"))
    instance_no = Column(String(100), nullable=False, unique=True)  # APR-2026-00001
    biz_type = Column(String(50), nullable=False)
    biz_id = Column(BigInteger, nullable=False)
    applicant_id = Column(BigInteger)
    applicant_name = Column(String(200))
    current_step = Column(Integer, default=1)
    status = Column(String(30), default="pending")  # pending/approved/rejected
    approval_chain = Column(JSONB, default=[])  # [{"step":1,"approver":"xxx","action":"approve","comment":"","time":""}]
    total_steps = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
