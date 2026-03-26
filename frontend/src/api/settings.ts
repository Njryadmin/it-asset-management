import request from './request'

export interface SystemSettings {
  system_name: string
  company_name: string
  contact_email: string
  contact_phone: string
  asset_code_prefix: string
  auto_backup: boolean
  backup_retention_days: number
}

export const settingsApi = {
  get() {
    return request.get<SystemSettings>('/settings')
  },
  
  update(data: Partial<SystemSettings>) {
    return request.put('/settings', data)
  },
  
  getAssetCodeConfig() {
    return request.get<{ prefix: string; example: string }>('/settings/asset-codes')
  }
}
