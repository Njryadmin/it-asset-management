import request from './request'
import type { ApiResponse, Category, CategoryForm } from '@/types'

export const categoriesApi = {
  list(params?: { keyword?: string; parent_id?: number; page?: number; page_size?: number }) {
    return request.get<ApiResponse<Category>>('/categories', { params })
  },
  
  getTree() {
    return request.get<Category[]>('/categories/tree')
  },
  
  get(id: number) {
    return request.get<Category>(`/categories/${id}`)
  },
  
  create(data: CategoryForm) {
    return request.post<Category>('/categories', data)
  },
  
  update(id: number, data: Partial<CategoryForm>) {
    return request.put<Category>(`/categories/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/categories/${id}`)
  }
}
