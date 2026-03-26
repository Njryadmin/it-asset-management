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
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

// Category types
export interface Category {
  id: number
  name: string
  code: string | null
  parent_id: number | null
  description: string | null
  created_at: string
  children?: Category[]
}

// Supplier types
export interface Supplier {
  id: number
  name: string
  code: string | null
  contact_person: string | null
  phone: string | null
  email: string | null
  address: string | null
  description: string | null
  is_active: boolean
  created_at: string
}

// Department types
export interface Department {
  id: number
  name: string
  code: string | null
  parent_id: number | null
  description: string | null
  created_at: string
  children?: Department[]
}

// Asset types
export type AssetStatus = 'in_use' | 'idle' | 'maintenance' | 'retired' | 'scrapped'

export interface Asset {
  id: number
  name: string
  asset_code: string
  serial_number: string | null
  category_id: number
  supplier_id: number | null
  department_id: number | null
  assigned_to: number | null
  status: AssetStatus
  purchase_date: string | null
  purchase_price: number | null
  warranty_expire_date: string | null
  description: string | null
  specs: string | null
  created_at: string
  updated_at: string | null
}

// Purchase Request types
export type PurchaseRequestStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'purchased'

export interface PurchaseRequest {
  id: number
  title: string
  description: string | null
  category_id: number | null
  supplier_id: number | null
  requester_id: number
  quantity: number
  estimated_price: number | null
  actual_price: number | null
  status: PurchaseRequestStatus
  approver_comment: string | null
  approved_at: string | null
  purchased_at: string | null
  created_at: string
}

// Dashboard types
export interface DashboardStats {
  total_assets: number
  total_categories: number
  total_suppliers: number
  total_departments: number
  total_users: number
  total_purchase_requests: number
  assets_by_status: Record<string, number>
  assets_by_category: Record<string, number>
  recent_assets: Asset[]
  pending_purchase_requests: PurchaseRequest[]
}

// Form types
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
}

export interface PurchaseRequestForm {
  title: string
  description?: string
  category_id?: number
  supplier_id?: number
  quantity: number
  estimated_price?: number
}

// Pagination
export interface PaginationParams {
  page: number
  page_size: number
  keyword?: string
  category_id?: number
  status?: string
  department_id?: number
}
