from sqlalchemy import Column, String, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String(200), default="IT资产管理系统")
    site_title = Column(String(200), default="IT资产管理系统")
    site_description = Column(Text, default="高效的IT资产管理系统")
    company_name = Column(String(200), default="")
    contact_email = Column(String(100), default="")
    contact_phone = Column(String(50), default="")
    asset_code_prefix = Column(String(50), default="ASSET")
    auto_backup = Column(Boolean, default=True)
    backup_retention_days = Column(Integer, default=30)
    logo_url = Column(Text, default="")
    favicon_url = Column(Text, default="")
    announcement = Column(Text, default="")
    announcement_enabled = Column(Boolean, default=False)
    version = Column(String(20), default="v2.0.0")
