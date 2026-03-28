<template>
  <div class="audit-page page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">审计日志</h3>
            <span class="item-count">共 {{ total }} 条</span>
          </div>
        </div>
      </template>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="资产操作" name="asset" />
        <el-tab-pane label="采购操作" name="purchase" />
        <el-tab-pane label="用户操作" name="user" />
      </el-tabs>

      <!-- Filter Bar -->
      <div class="filter-bar">
        <el-select v-model="filterParams.action" placeholder="操作类型" clearable style="width: 140px" @change="fetchLogs">
          <el-option label="创建" value="CREATE" />
          <el-option label="更新" value="UPDATE" />
          <el-option label="删除" value="DELETE" />
          <el-option label="审批通过" value="APPROVE" />
          <el-option label="审批拒绝" value="REJECT" />
        </el-select>
        <el-input v-model="filterParams.actor_name" placeholder="操作人" clearable style="width: 140px" @change="fetchLogs" />
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 240px"
          @change="onDateChange"
        />
        <el-input v-model="filterParams.biz_type" placeholder="资源类型" clearable style="width: 140px" @change="fetchLogs" />
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="fetchLogs">查询</el-button>
      </div>

      <!-- Table -->
      <el-table
        v-loading="loading"
        :data="logs"
        style="width: 100%"
        row-key="id"
        :expand-row-keys="expandedIds"
        @expand-change="onExpandChange"
      >
        <el-table-column type="expand" width="50">
          <template #default="{ row }">
            <div class="expand-content" v-if="expandedIds.includes(row.id)">
              <div class="expand-section">
                <div class="expand-label">变更前 (before_state)</div>
                <pre class="json-block json-before">{{ formatJson(row.beforeState) }}</pre>
              </div>
              <div class="expand-section">
                <div class="expand-label">变更后 (after_state)</div>
                <pre class="json-block json-after">{{ formatJson(row.afterState) }}</pre>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="170">
          <template #default="{ row }">
            {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm:ss') }}
          </template>
        </el-table-column>
        <el-table-column prop="actorName" label="操作人" width="120">
          <template #default="{ row }">
            {{ row.actorName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="110">
          <template #default="{ row }">
            <el-tag :type="actionTagType(row.action)" size="small">{{ actionLabel(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bizTypeLabel" label="资源类型" width="120" />
        <el-table-column prop="bizId" label="资源ID" width="100">
          <template #default="{ row }">
            {{ row.bizId ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="changeSummary" label="变更摘要" min-width="200" show-overflow-tooltip />
        <el-table-column label="详情" width="80" align="center">
          <template #default="{ row }">
            <span class="action-link" @click="toggleExpand(row.id)">
              <el-icon><View /></el-icon>
              <span>查看</span>
            </span>
          </template>
        </el-table-column>
      </el-table>

      <!-- Empty state -->
      <el-empty v-if="!loading && logs.length === 0" description="暂无审计日志" />

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filterParams.page"
          :page-size="filterParams.page_size"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { auditApi, type AuditLogItem } from '@/api/auditApi'
import dayjs from 'dayjs'

const activeTab = ref('all')
const loading = ref(false)
const logs = ref<AuditLogItem[]>([])
const total = ref(0)
const expandedIds = ref<number[]>([])
const dateRange = ref<string[]>([])

const filterParams = reactive({
  action: '',
  actor_name: '',
  biz_type: '',
  start_date: '',
  end_date: '',
  page: 1,
  page_size: 20
})

const tabResourceTypeMap: Record<string, string> = {
  all: '',
  asset: 'assets',
  purchase: 'purchase_request',
  user: 'users'
}

function onTabChange() {
  filterParams.biz_type = tabResourceTypeMap[activeTab.value]
  filterParams.page = 1
  fetchLogs()
}

function onDateChange(val: string[] | null) {
  if (val && val.length === 2) {
    filterParams.start_date = val[0]
    filterParams.end_date = val[1]
  } else {
    filterParams.start_date = ''
    filterParams.end_date = ''
  }
  fetchLogs()
}

function toggleExpand(id: number) {
  const idx = expandedIds.value.indexOf(id)
  if (idx > -1) {
    expandedIds.value.splice(idx, 1)
  } else {
    expandedIds.value = [id]
  }
}

function onExpandChange(row: AuditLogItem) {
  const id = row.id
  const idx = expandedIds.value.indexOf(id)
  if (idx > -1) {
    expandedIds.value.splice(idx, 1)
  } else {
    expandedIds.value = [id]
  }
}

async function fetchLogs() {
  loading.value = true
  try {
    const params: Record<string, any> = { ...filterParams }
    // remove empty strings
    Object.keys(params).forEach(k => {
      if (params[k] === '') delete params[k]
    })
    const res = await auditApi.list(params)
    logs.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  activeTab.value = 'all'
  filterParams.action = ''
  filterParams.actor_name = ''
  filterParams.biz_type = ''
  filterParams.start_date = ''
  filterParams.end_date = ''
  filterParams.page = 1
  dateRange.value = []
  fetchLogs()
}

function actionLabel(row: AuditLogItem) {
  return row.actionLabel || row.action
}

function actionTagType(action: string) {
  const map: Record<string, string> = {
    CREATE: 'success',
    UPDATE: 'primary',
    DELETE: 'danger',
    APPROVE: 'success',
    REJECT: 'danger'
  }
  return map[action] || 'info'
}

function formatJson(obj: Record<string, any> | null): string {
  if (!obj) return '(无)'
  return JSON.stringify(obj, null, 2)
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.audit-page {
  max-width: 1400px;
  margin: 0 auto;
}

.main-card {
  border-radius: var(--radius-lg) !important;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--wechat-text);
}

.item-count {
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  align-items: center;
}

.expand-content {
  padding: 12px 20px;
  display: flex;
  gap: 20px;
  background: var(--wechat-bg);
}

.expand-section {
  flex: 1;
  min-width: 0;
}

.expand-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--wechat-text-secondary);
  margin-bottom: 6px;
}

.json-block {
  background: var(--wechat-card);
  border: 1px solid var(--wechat-border-light);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: var(--wechat-text);
  overflow: auto;
  max-height: 200px;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
