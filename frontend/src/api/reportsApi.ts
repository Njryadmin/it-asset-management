import request from './request'

// 后端返回 snake_case，经拦截器转换为 camelCase

export interface AssetSummary {
  total: number
  byStatus: Record<string, number>
  byCategory: { name: string; value: number }[]
  byDepartment: { name: string; value: number }[]
  byImportance: Record<string, number>
  thisMonthNew: number
  thisMonthRetired: number
}

export interface DistributionResponse {
  byCategory: { name: string; value: number }[]
  byStatus: { name: string; value: number }[]
  byDepartment: { name: string; value: number }[]
  byImportance: { name: string; value: number }[]
}

export interface TrendResponse {
  items: { month: string; added: number; retired: number }[]
}

export interface PurchaseSummary {
  totalCount: number
  totalAmount: number
  byStatus: Record<string, number>
  bySupplier: { name: string; value: number }[]
  thisMonthCount: number
  thisMonthAmount: number
}

export const reportsApi = {
  assetSummary(params?: { department_id?: number; category_id?: number }) {
    return request.get<AssetSummary>('/reports/assets/summary', { params })
  },
  assetDistribution(params?: { category_id?: number; department_id?: number }) {
    return request.get<DistributionResponse>('/reports/assets/distribution', { params })
  },
  assetTrend(params?: { months?: number }) {
    return request.get<TrendResponse>('/reports/assets/trend', { params })
  },
  purchaseSummary(params?: { start_date?: string; end_date?: string }) {
    return request.get<PurchaseSummary>('/reports/purchases/summary', { params })
  }
}
