import request from './request'

export interface AssetTransferLogItem {
  id: number
  assetId: number
  assetName: string | null
  fromUserId: number | null
  fromUserName: string | null
  toUserId: number | null
  toUserName: string | null
  fromDepartmentId: number | null
  fromDepartmentName: string | null
  toDepartmentId: number | null
  toDepartmentName: string | null
  transferType: string
  reason: string | null
  operatorId: number
  operatorName: string | null
  createdAt: string
}

export interface TransferRequest {
  asset_id: number
  to_user_id?: number
  to_department_id?: number
  reason?: string
}

export const assetTransfersApi = {
  /**
   * 创建资产转移/分配记录
   */
  create(params: TransferRequest) {
    return request.post('/asset-transfers', params)
  },

  /**
   * 获取资产的转移历史
   */
  getAssetHistory(assetId: number) {
    return request.get<AssetTransferLogItem[]>(`/asset-transfers/asset/${assetId}`)
  },

  /**
   * 获取转移记录列表
   */
  list(params?: { page?: number; page_size?: number; keyword?: string }) {
    return request.get<AssetTransferLogItem[]>('/asset-transfers', { params })
  }
}
