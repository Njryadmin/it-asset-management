import request from './request'

export interface AuditLogItem {
  id: number
  bizType: string
  bizId: number | null
  action: 'CREATE' | 'UPDATE' | 'DELETE' | 'APPROVE' | 'REJECT'
  assetCode: string | null
  actorId: number | null
  actorName: string | null
  actorIp: string | null
  beforeState: Record<string, any> | null
  afterState: Record<string, any> | null
  changeSummary: string | null
  createdAt: string
}

export const auditApi = {
  list(params?: {
    action?: string
    actor_id?: number
    biz_type?: string
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
    keyword?: string
  }) {
    return request.get<{ items: AuditLogItem[]; total: number }>('/audit-logs', { params })
  },
  detail(id: number) {
    return request.get<AuditLogItem>(`/audit-logs/${id}`)
  }
}
