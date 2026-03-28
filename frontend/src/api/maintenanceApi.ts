import request from './request'

export interface MaintenanceLog {
  id: number
  asset_id: number
  maintenance_type: string
  maintenance_date: string
  vendor?: string
  cost?: number
  description?: string
  next_maintenance_date?: string
  created_by?: number
  created_at?: string
  asset_name?: string
}

export interface MaintenanceLogForm {
  asset_id: number
  maintenance_type: string
  maintenance_date: string
  vendor?: string
  cost?: number
  description?: string
  next_maintenance_date?: string
}

export const maintenanceApi = {
  list(params: { asset_id?: number; page?: number; page_size?: number }) {
    return request.get<{ total: number; items: MaintenanceLog[] }>('/asset-maintenance-logs', { params })
  },
  create(data: MaintenanceLogForm) {
    return request.post('/asset-maintenance-logs', data)
  },
  update(id: number, data: Partial<MaintenanceLogForm>) {
    return request.put(`/asset-maintenance-logs/${id}`, data)
  },
  delete(id: number) {
    return request.delete(`/asset-maintenance-logs/${id}`)
  }
}
