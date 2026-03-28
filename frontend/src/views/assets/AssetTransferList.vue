<template>
  <div class="asset-transfer-list">
    <div class="page-header">
      <h2>资产转移记录</h2>
    </div>

    <!-- Search -->
    <el-card class="filter-card">
      <el-form inline @submit.prevent="handleSearch">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索资产名称/原因" clearable @clear="handleSearch" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <el-table :data="transfers" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="assetName" label="资产名称" min-width="150">
          <template #default="{ row }">
            <router-link :to="`/assets/${row.assetId}`" class="asset-link">
              {{ row.assetName }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column label="转移类型" width="100">
          <template #default="{ row }">
            <el-tag :type="transferTypeTag(row.transferType)">
              {{ transferTypeLabel(row.transferType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="原使用人" width="120">
          <template #default="{ row }">
            {{ row.fromUserName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="新使用人" width="120">
          <template #default="{ row }">
            {{ row.toUserName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="原部门" width="120">
          <template #default="{ row }">
            {{ row.fromDepartmentName || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="新部门" width="120">
          <template #default="{ row }">
            {{ row.toDepartmentName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="转移原因" min-width="150" show-overflow-tooltip />
        <el-table-column prop="operatorName" label="操作人" width="100" />
        <el-table-column prop="createdAt" label="时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
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
import { assetTransfersApi, type AssetTransferLogItem } from '@/api/assetTransfers'

const loading = ref(false)
const transfers = ref<AssetTransferLogItem[]>([])

const filters = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN')
}

function transferTypeLabel(type: string) {
  const map: Record<string, string> = {
    transfer: '转移',
    assign: '分配',
    revoke: '收回'
  }
  return map[type] || type
}

function transferTypeTag(type: string) {
  const map: Record<string, string> = {
    transfer: 'warning',
    assign: 'success',
    revoke: 'info'
  }
  return map[type] || ''
}

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: filters.keyword || undefined
    }
    const res = await assetTransfersApi.list(params)
    transfers.value = res.data
    pagination.total = res.data?.length || 0
  } catch (error: any) {
    ElMessage.error('获取转移记录失败')
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
.asset-transfer-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.filter-card {
  margin-bottom: 16px;
}

.asset-link {
  color: var(--el-color-primary);
  text-decoration: none;
}

.asset-link:hover {
  text-decoration: underline;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
