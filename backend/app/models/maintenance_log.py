from sqlalchemy import Column, BigInteger, String, Text, Date, DateTime, Numeric, ForeignKey, func
from app.core.database import Base


class AssetMaintenanceLog(Base):
    __tablename__ = "asset_maintenance_logs"
    id = Column(BigInteger, primary_key=True)
    asset_id = Column(BigInteger, ForeignKey("assets.id"), nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    maintenance_date = Column(Date, nullable=False)
    vendor = Column(String(200))
    cost = Column(Numeric(12, 2))
    description = Column(Text)
    next_maintenance_date = Column(Date)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
