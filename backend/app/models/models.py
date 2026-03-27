from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Float, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    assets = relationship("Asset", back_populates="assigned_to_user")
    purchase_requests = relationship("PurchaseRequest", back_populates="requester")
    department = relationship("Department", back_populates="users")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    parent = relationship("Category", remote_side=[id], backref="children")
    assets = relationship("Asset", back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assets = relationship("Asset", back_populates="supplier")
    purchase_requests = relationship("PurchaseRequest", back_populates="supplier")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    parent = relationship("Department", remote_side=[id], backref="children")
    assets = relationship("Asset", back_populates="department")
    users = relationship("User", back_populates="department")


class AssetStatus(str, enum.Enum):
    IN_USE = "in_use"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"
    SCRAPPED = "scrapped"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    asset_code = Column(String(100), unique=True, index=True, nullable=False)
    serial_number = Column(String(100), unique=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    status = Column(Enum(AssetStatus), default=AssetStatus.IDLE, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    purchase_price = Column(Float, nullable=True)
    warranty_expire_date = Column(DateTime(timezone=True), nullable=True)
    
    description = Column(Text)
    specs = Column(Text)  # JSON string for specifications
    region = Column(String(100), nullable=True)  # 地区
    
    # New fields
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    purchase_date = Column(Date, nullable=True)  # Plain date without time
    importance_level = Column(String(20), nullable=True)  # critical/important/normal/low
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="assets")
    supplier = relationship("Supplier", back_populates="assets")
    department = relationship("Department", back_populates="assets")
    assigned_to_user = relationship("User", back_populates="assets")


class PurchaseRequestStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PURCHASED = "purchased"


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    quantity = Column(Integer, default=1)
    estimated_price = Column(Float, nullable=True)
    actual_price = Column(Float, nullable=True)
    
    status = Column(Enum(PurchaseRequestStatus), default=PurchaseRequestStatus.DRAFT, nullable=False)
    
    approver_comment = Column(Text)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    purchased_at = Column(DateTime(timezone=True), nullable=True)
    
    region = Column(String(100), nullable=True)  # 采购地区
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category")
    supplier = relationship("Supplier", back_populates="purchase_requests")
    requester = relationship("User", back_populates="purchase_requests")
