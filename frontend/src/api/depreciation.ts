import request from './request'

export interface DepreciationItem {
  assetId: number
  assetName: string
  assetCode: string
  purchaseDate: string
  asOfDate: string
  method: string
  depreciationYears: number
  originalValue: number
  currentValue: number
  accumulatedDepreciation: number
  depreciationRate: number
  usedYears: number
  netValueRate: number
  annualDepreciation: number
  salvageValue: number
  remainingYears: number
}

export interface DepreciationSummary {
  totalOriginalValue: number
  totalCurrentValue: number
  totalAccumulatedDepreciation: number
  totalDepreciationRate: number
}

export interface DepreciationResponse {
  items: DepreciationItem[]
  total: number
  summary: DepreciationSummary
}

export const depreciationApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string; as_of_date?: string }) {
    return request.get<DepreciationResponse>('/depreciation/list', { params })
  },

  getAsset(assetId: number, asOfDate?: string) {
    return request.get<DepreciationItem>(`/depreciation/asset/${assetId}`, {
      params: asOfDate ? { as_of_date: asOfDate } : undefined
    })
  }
}
