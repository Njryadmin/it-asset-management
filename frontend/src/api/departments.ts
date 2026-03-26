import request from './request'
import type { Department } from '@/types'

export interface DepartmentForm {
  name: string
  code?: string
  parent_id?: number
  description?: string
}

export const departmentsApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string }) {
    return request.get<{ total: number; items: Department[] }>('/departments', { params })
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
