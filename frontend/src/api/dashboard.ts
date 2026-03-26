import request from './request'
import type { DashboardStats } from '@/types'

export const dashboardApi = {
  getStats() {
    return request.get<DashboardStats>('/dashboard/stats')
  }
}
