// API Response types
export interface ApiResponse<T = any> {
  total: number
  items: T[]
}

export interface ApiError {
  detail: string
}

// User types
export interface User {
  id: number
  username: string
  email: string
  fullName: string | null
  isActive: boolean
  isSuperuser: boolean
  createdAt: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
  full_name?: string
  is_superuser?: boolean
}

export interface UserUpdate {
  email?: string
  full_name?: string
  password?: string
  is_superuser?: boolean
  is_active?: boolean
}

export interface UserListResponse {
  total: number
  items: User[]
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  accessToken: string
  tokenType: string
}

// Category types
export interface Category {
  id: number
  name: string
  code: string | null
  parentId: number | null
  description: string | null
  createdAt: string
  children?: Category[]
}

// Supplier types
export interface Supplier {
  id: number
  name: string
  code: string | null
  contactPerson: string | null
  phone: string | null
  email: string | null
  address: string | null
  description: string | null
  isActive: boolean
  createdAt: string
}

// Department types
export interface Department {
  id: number
  name: string
  code: string | null
  parentId: number | null
  description: string | null
  createdAt: string
  children?: Department[]
}

// Asset types
export type AssetStatus = 'in_use' | 'idle' | 'maintenance' | 'retired' | 'scrapped'

export interface Asset {
  id: number
  name: string
  assetCode: string
  serialNumber: string | null
  categoryId: number
  supplierId: number | null
  departmentId: number | null
  assignedTo: number | null
  status: AssetStatus
  purchaseDate: string | null
  purchasePrice: number | null
  warrantyExpireDate: string | null
  description: string | null
  specs: string | null
  region: string | null
  createdAt: string
  updatedAt: string | null
}

// Purchase Request types
export type PurchaseRequestStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'purchased'

export interface PurchaseRequest {
  id: number
  title: string
  description: string | null
  categoryId: number | null
  supplierId: number | null
  requesterId: number
  quantity: number
  estimatedPrice: number | null
  actualPrice: number | null
  status: PurchaseRequestStatus
  approverComment: string | null
  approvedAt: string | null
  purchasedAt: string | null
  createdAt: string
  region: string | null
}

// Dashboard types
export interface DashboardStats {
  totalAssets: number
  totalCategories: number
  totalSuppliers: number
  totalDepartments: number
  totalUsers: number
  totalPurchaseRequests: number
  assetsByStatus: Record<string, number>
  assetsByCategory: Record<string, number>
  recentAssets: Asset[]
  pendingPurchaseRequests: PurchaseRequest[]
}

// Form types (for API requests - these are snake_case since sent to API)
export interface CategoryForm {
  name: string
  code?: string
  parent_id?: number
  description?: string
}

export interface SupplierForm {
  name: string
  code?: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
  description?: string
}

export interface DepartmentForm {
  name: string
  code?: string
  parent_id?: number
  description?: string
}

export interface AssetForm {
  name: string
  asset_code: string
  serial_number?: string
  category_id: number
  supplier_id?: number
  department_id?: number
  assigned_to?: number
  status: AssetStatus
  purchase_date?: string
  purchase_price?: number
  warranty_expire_date?: string
  description?: string
  specs?: string
  region?: string
}

export interface PurchaseRequestForm {
  title: string
  description?: string
  category_id?: number
  supplier_id?: number
  quantity: number
  estimated_price?: number
  region?: string
}

// Pagination (params for API - snake_case since sent to API)
export interface PaginationParams {
  page: number
  page_size: number
  keyword?: string
  category_id?: number
}
