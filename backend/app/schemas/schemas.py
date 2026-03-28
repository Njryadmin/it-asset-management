from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date


# ============ User Schemas ============
class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str
    is_superuser: bool = False


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserListResponse(BaseModel):
    total: int
    items: List[UserResponse]


# ============ Auth Schemas ============
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ============ Category Schemas ============
class CategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    children: List["CategoryResponse"] = []


# ============ Supplier Schemas ============
class SupplierBase(BaseModel):
    name: str
    code: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime


# ============ Department Schemas ============
class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    children: List["DepartmentResponse"] = []


# ============ Asset Schemas ============
class AssetBase(BaseModel):
    name: str
    asset_code: str
    serial_number: Optional[str] = None
    category_id: int
    supplier_id: Optional[int] = None
    department_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: str = "idle"
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    warranty_expire_date: Optional[datetime] = None
    description: Optional[str] = None
    specs: Optional[str] = None
    region: Optional[str] = None
    # New fields
    brand: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    importance_level: Optional[str] = None
    depreciation_years: Optional[int] = None
    depreciation_method: Optional[str] = None
    salvage_rate: Optional[float] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_code: Optional[str] = None
    serial_number: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    department_id: Optional[int] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    warranty_expire_date: Optional[datetime] = None
    description: Optional[str] = None
    specs: Optional[str] = None
    region: Optional[str] = None
    # New fields
    brand: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    importance_level: Optional[str] = None


class AssetResponse(AssetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class AssetListResponse(BaseModel):
    total: int
    items: List[AssetResponse]


# ============ Purchase Request Schemas ============
class PurchaseRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    quantity: int = 1
    estimated_price: Optional[float] = None
    region: Optional[str] = None


class PurchaseRequestCreate(PurchaseRequestBase):
    pass


class PurchaseRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    quantity: Optional[int] = None
    estimated_price: Optional[float] = None
    actual_price: Optional[float] = None
    status: Optional[str] = None
    approver_comment: Optional[str] = None
    region: Optional[str] = None


class PurchaseRequestResponse(PurchaseRequestBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    requester_id: int
    status: str
    actual_price: Optional[float] = None
    approver_comment: Optional[str] = None
    approved_at: Optional[datetime] = None
    purchased_at: Optional[datetime] = None
    created_at: datetime
    region: Optional[str] = None


class PurchaseRequestListResponse(BaseModel):
    total: int
    items: List[PurchaseRequestResponse]


# ============ Dashboard Schemas ============
class DashboardStats(BaseModel):
    total_assets: int
    total_categories: int
    total_suppliers: int
    total_departments: int
    total_users: int
    total_purchase_requests: int
    
    assets_by_status: dict
    assets_by_category: dict
    recent_assets: List[AssetResponse]
    pending_purchase_requests: List[PurchaseRequestResponse]


# ============ Common ============
class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class ListResponse(BaseModel):
    total: int
    items: List


CategoryResponse.model_rebuild()
DepartmentResponse.model_rebuild()


# Asset Transfer Log schemas
class AssetTransferLogBase(BaseModel):
    asset_id: int
    from_user_id: int | None = None
    to_user_id: int | None = None
    from_department_id: int | None = None
    to_department_id: int | None = None
    transfer_type: str  # assign, transfer, revoke
    reason: str | None = None


class AssetTransferLogCreate(AssetTransferLogBase):
    pass


class AssetTransferLogResponse(AssetTransferLogBase):
    id: int
    operator_id: int
    created_at: datetime
    asset_name: str | None = None
    from_user_name: str | None = None
    to_user_name: str | None = None
    from_department_name: str | None = None
    to_department_name: str | None = None
    operator_name: str | None = None

    class Config:
        from_attributes = True


class AssetTransferRequest(BaseModel):
    """资产转移/分配请求"""
    asset_id: int
    to_user_id: int | None = None
    to_department_id: int | None = None
    reason: str | None = None
