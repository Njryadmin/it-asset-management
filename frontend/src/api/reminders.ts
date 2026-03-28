import request from './request'

export interface WarrantyExpiringItem {
  id: number
  name: string
  assetCode: string
  warrantyExpireDate: string
  daysRemaining: number | null
  status: string
}

export interface MaintenanceDueItem {
  id: number
  name: string
  assetCode: string
  maintenanceType: string
  nextMaintenanceDate: string
  daysRemaining: number | null
  lastMaintenanceDate: string | null
  lastMaintenanceVendor: string | null
}

export interface ReminderSummary {
  warrantyExpiring7Days: number
  warrantyExpiring30Days: number
  maintenanceDue30Days: number
}

export const remindersApi = {
  getSummary() {
    return request.get<ReminderSummary>('/reminders/summary')
  },

  getWarrantyExpiring(days: number = 30) {
    return request.get<{ total: number; items: WarrantyExpiringItem[] }>('/reminders/warranty-expiring', { params: { days } })
  },

  getMaintenanceDue(days: number = 30) {
    return request.get<{ total: number; items: MaintenanceDueItem[] }>('/reminders/maintenance-due', { params: { days } })
  }
}
