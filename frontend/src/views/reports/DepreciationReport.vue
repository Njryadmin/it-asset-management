<template>
  <div class="depreciation-page">
    <div class="page-header">
      <h2>资产折旧报表</h2>
      <el-tag type="info">截止日期: {{ asOfDate }}</el-tag>
    </div>

    <!-- Summary Cards -->
    <el-row :gutter="12" class="summary-row">
      <el-col :xs="12" :sm="6">
        <div class="summary-card">
          <div class="summary-label">资产原值</div>
          <div class="summary-value">¥{{ formatNumber(summary.totalOriginalValue) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="summary-card">
          <div class="summary-label">当前净值</div>
          <div class="summary-value highlight">¥{{ formatNumber(summary.totalCurrentValue) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="summary-card">
          <div class="summary-label">累计折旧</div>
          <div class="summary-value danger">-¥{{ formatNumber(summary.totalAccumulatedDepreciation) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="summary-card">
          <div class="summary-label">平均折旧率</div>
          <div class="summary-value">{{ summary.totalDepreciationRate }}%</div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter -->
    <el-card class="filter-card">
      <el-form class="filter-form" inline>
        <el-form-item label="截止日期">
          <el-date-picker v-model="asOfDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" @change="fetchData" />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="资产名称/编号" clearable @clear="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <div class="table-scroll">
      <el-table :data="depreciations" v-loading="loading" stripe>
        <el-table-column prop="assetName" label="资产名称" min-width="150">
          <template #default="{ row }">
            <router-link :to="`/assets/${row.assetId}`" class="asset-link">{{ row.assetName }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="assetCode" label="资产编号" width="130" />
        <el-table-column prop="purchaseDate" label="购买日期" width="110" />
        <el-table-column prop="method" label="折旧方法" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.method === 'straight-line' ? '直线法' : '双倍余额' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="originalValue" label="原值(元)" width="120" align="right">
          <template #default="{ row }">{{ formatNumber(row.originalValue) }}</template>
        </el-table-column>
        <el-table-column prop="accumulatedDepreciation" label="累计折旧" width="120" align="right">
          <template #default="{ row }">
            <span class="text-danger">-{{ formatNumber(row.accumulatedDepreciation) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="currentValue" label="当前净值" width="120" align="right">
          <template #default="{ row }">
            <strong>{{ formatNumber(row.currentValue) }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="depreciationRate" label="折旧率" width="80" align="right">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(row.depreciationRate, 100)" :stroke-width="10" :show-text="false" />
            <span class="progress-text">{{ row.depreciationRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="usedYears" label="已用年限" width="80" align="right">
          <template #default="{ row }">{{ row.usedYears }}年</template>
        </el-table-column>
        <el-table-column prop="remainingYears" label="剩余年限" width="80" align="right">
          <template #default="{ row }">{{ row.remainingYears }}年</template>
        </el-table-column>
      </el-table>
      </div>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { depreciationApi, type DepreciationItem, type DepreciationSummary } from '@/api/depreciation'
import dayjs from 'dayjs'

const loading = ref(false)
const depreciations = ref<DepreciationItem[]>([])
const summary = ref<DepreciationSummary>({ totalOriginalValue: 0, totalCurrentValue: 0, totalAccumulatedDepreciation: 0, totalDepreciationRate: 0 })

const filters = reactive({ keyword: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const asOfDate = ref(dayjs().format('YYYY-MM-DD'))

function formatNumber(num: number) {
  return num?.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '0.00'
}

async function fetchData() {
  loading.value = true
  try {
    const res = await depreciationApi.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: filters.keyword || undefined,
      as_of_date: asOfDate.value
    })
    depreciations.value = res.data.items
    pagination.total = res.data.total
    summary.value = res.data.summary
  } catch (e) {
    ElMessage.error('获取折旧数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function resetFilters() {
  filters.keyword = ''
  pagination.page = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.depreciation-page { padding: 16px; }
.page-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.page-header h2 { margin: 0; font-size: 18px; }
.summary-row { margin-bottom: 12px; }
.summary-card { background: var(--wechat-card-bg, #fff); border-radius: 8px; padding: 14px 10px; text-align: center; }
.summary-label { font-size: 11px; color: #888; margin-bottom: 6px; }
.summary-value { font-size: 18px; font-weight: 700; }
.summary-value.highlight { color: var(--el-color-success); }
.summary-value.danger { color: var(--el-color-danger); }
.filter-card { margin-bottom: 12px; }
.asset-link { color: var(--el-color-primary); text-decoration: none; }
.asset-link:hover { text-decoration: underline; }
.text-danger { color: var(--el-color-danger); }
.progress-text { font-size: 11px; color: #888; margin-top: 2px; display: block; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.table-scroll :deep(.el-table) { min-width: 900px; }
@media (max-width: 768px) {
  .depreciation-page { padding: 12px; }
  .page-header h2 { font-size: 16px; }
  .filter-form { display: flex; flex-direction: column; gap: 8px; }
  .filter-form .el-form-item { margin-bottom: 0; }
  .summary-value { font-size: 16px; }
}
@media (max-width: 480px) {
  .depreciation-page { padding: 8px; }
  .page-header { flex-wrap: wrap; }
  .page-header h2 { font-size: 15px; }
  .summary-card { padding: 12px 8px; }
  .summary-value { font-size: 15px; }
  .pagination { justify-content: center; }
}
</style>
