import request from './request'
import type { ApiResponse, PurchaseRequest, PurchaseRequestForm } from '@/types'

export const purchasesApi = {
  list(params?: { keyword?: string; status?: string; page?: number; page_size?: number }) {
    return request.get<ApiResponse<PurchaseRequest>>('/purchase-requests', { params })
  },
  
  getPending() {
    return request.get<PurchaseRequest[]>('/purchase-requests/pending')
  },
  
  get(id: number) {
    return request.get<PurchaseRequest>(`/purchase-requests/${id}`)
  },
  
  create(data: PurchaseRequestForm) {
    return request.post<PurchaseRequest>('/purchase-requests', data)
  },
  
  update(id: number, data: Partial<PurchaseRequestForm>) {
    return request.put<PurchaseRequest>(`/purchase-requests/${id}`, data)
  },
  
  submit(id: number) {
    return request.post(`/purchase-requests/${id}/submit`)
  },
  
  approve(id: number, comment?: string) {
    return request.post(`/purchase-requests/${id}/approve`, { comment })
  },
  
  reject(id: number, comment?: string) {
    return request.post(`/purchase-requests/${id}/reject`, { comment })
  },
  
  markPurchased(id: number, actual_price?: number) {
    return request.post(`/purchase-requests/${id}/purchase`, { actual_price })
  },
  
  delete(id: number) {
    return request.delete(`/purchase-requests/${id}`)
  }
}
