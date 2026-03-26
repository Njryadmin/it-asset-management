import request from './request'
import type { ApiResponse, Supplier, SupplierForm } from '@/types'

export const suppliersApi = {
  list(params?: { keyword?: string; is_active?: boolean; page?: number; page_size?: number }) {
    return request.get<ApiResponse<Supplier>>('/suppliers', { params })
  },
  
  get(id: number) {
    return request.get<Supplier>(`/suppliers/${id}`)
  },
  
  create(data: SupplierForm) {
    return request.post<Supplier>('/suppliers', data)
  },
  
  update(id: number, data: Partial<SupplierForm>) {
    return request.put<Supplier>(`/suppliers/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/suppliers/${id}`)
  }
}
