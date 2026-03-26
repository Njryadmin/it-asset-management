import request from './request'
import type { ApiResponse, Department, DepartmentForm } from '@/types'

export const departmentsApi = {
  list(params?: { keyword?: string; parent_id?: number; page?: number; page_size?: number }) {
    return request.get<ApiResponse<Department>>('/departments', { params })
  },
  
  getTree() {
    return request.get<Department[]>('/departments/tree')
  },
  
  get(id: number) {
    return request.get<Department>(`/departments/${id}`)
  },
  
  create(data: DepartmentForm) {
    return request.post<Department>('/departments', data)
  },
  
  update(id: number, data: Partial<DepartmentForm>) {
    return request.put<Department>(`/departments/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/departments/${id}`)
  }
}
