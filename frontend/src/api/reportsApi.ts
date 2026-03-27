import request from './request'

export interface AssetSummary {
  total: number
  inUse: number
  idle: number
  maintenance: number
  retired: number
  scrapped: number
  addedThisMonth: number
  scrappedThisMonth: number
}

export interface CategoryDistribution {
  name: string
  value: number
}

export interface StatusDistribution {
  status: string
  label: string
  count: number
}

export interface DepartmentDistribution {
  name: string
  count: number
}

export interface TrendPoint {
  month: string
  count: number
}

export const reportsApi = {
  assetSummary(params?: { start_date?: string; end_date?: string }) {
    return request.get<AssetSummary>('/reports/assets/summary', { params })
  },
  assetDistribution(params?: { category_id?: number; department_id?: number }) {
    return request.get<{
      byCategory: CategoryDistribution[]
      byStatus: StatusDistribution[]
      byDepartment: DepartmentDistribution[]
    }>('/reports/assets/distribution', { params })
  },
  assetTrend(params?: { months?: number }) {
    return request.get<TrendPoint[]>('/reports/assets/trend', { params })
  },
  purchaseSummary(params?: { start_date?: string; end_date?: string }) {
    return request.get('/reports/purchases/summary', { params })
  }
}
