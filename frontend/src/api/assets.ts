import request from './request'
import type { ApiResponse, Asset, AssetForm } from '@/types'

export const assetsApi = {
  list(params?: { 
    keyword?: string; 
    category_id?: number; 
    status?: string; 
    department_id?: number;
    page?: number; 
    page_size?: number 
  }) {
    return request.get<ApiResponse<Asset>>('/assets', { params })
  },
  
  getStats() {
    return request.get('/assets/stats')
  },
  
  get(id: number) {
    return request.get<Asset>(`/assets/${id}`)
  },
  
  create(data: AssetForm) {
    return request.post<Asset>('/assets', data)
  },
  
  update(id: number, data: Partial<AssetForm>) {
    return request.put<Asset>(`/assets/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/assets/${id}`)
  }
}
