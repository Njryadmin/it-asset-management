import request from './request'

export interface SystemSettings {
  system_name: string
  site_title: string
  site_description: string
  company_name: string
  contact_email: string
  contact_phone: string
  asset_code_prefix: string
  auto_backup: boolean
  backup_retention_days: number
  logo_url: string
  favicon_url: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  full_name: string | null
  is_superuser: boolean
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
  },
  
  getThemes() {
    return request.get<Record<string, any>>('/settings/themes')
  },
  
  getProfile() {
    return request.get<UserProfile>('/settings/profile')
  },
  
  updateProfile(data: { email?: string; full_name?: string }) {
    return request.put('/settings/profile', data)
  },
  
  changePassword(oldPassword: string, newPassword: string) {
    return request.put('/settings/password', null, {
      params: { old_password: oldPassword, new_password: newPassword }
    })
  },
  
  uploadLogo(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<{ url: string }>('/settings/upload-logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  uploadFavicon(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<{ url: string }>('/settings/upload-favicon', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}
