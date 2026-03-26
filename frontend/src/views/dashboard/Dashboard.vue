<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Box /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalAssets || 0 }}</div>
              <div class="stat-label">资产总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><Grid /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCategories || 0 }}</div>
              <div class="stat-label">资产分类</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><Shop /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalSuppliers || 0 }}</div>
              <div class="stat-label">供应商</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><ShoppingCart /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalPurchaseRequests || 0 }}</div>
              <div class="stat-label">采购申请</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>资产状态分布</span>
          </template>
          <div class="status-list">
            <div v-for="(count, status) in stats.assetsByStatus" :key="status" class="status-item">
              <span class="status-name">{{ statusLabel(status) }}</span>
              <el-progress :percentage="getPercentage(count)" :color="statusColor(status)" />
              <span class="status-count">{{ count }}</span>
            </div>
            <el-empty v-if="!stats.assetsByStatus || Object.keys(stats.assetsByStatus).length === 0" description="暂无数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待审批采购申请</span>
          </template>
          <el-table :data="stats.pendingPurchaseRequests" style="width: 100%">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="quantity" label="数量" width="60" />
            <el-table-column prop="estimatedPrice" label="预估价格" width="100">
              <template #default="{ row }">
                {{ row.estimatedPrice ? `¥${row.estimatedPrice}` : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="申请时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.createdAt) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!stats.pendingPurchaseRequests || stats.pendingPurchaseRequests.length === 0" description="暂无待审批申请" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>最近添加的资产</span>
          </template>
          <el-table :data="stats.recentAssets" style="width: 100%">
            <el-table-column prop="name" label="资产名称" />
            <el-table-column prop="assetCode" label="资产编号" width="140" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="purchasePrice" label="购买价格" width="100">
              <template #default="{ row }">
                {{ row.purchasePrice ? `¥${row.purchasePrice}` : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="添加时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.createdAt) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!stats.recentAssets || stats.recentAssets.length === 0" description="暂无资产" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import type { DashboardStats } from '@/types'
import dayjs from 'dayjs'

const stats = ref<DashboardStats>({
  totalAssets: 0,
  totalCategories: 0,
  totalSuppliers: 0,
  totalDepartments: 0,
  totalUsers: 0,
  totalPurchaseRequests: 0,
  assetsByStatus: {},
  assetsByCategory: {},
  recentAssets: [],
  pendingPurchaseRequests: []
})

const statusMap: Record<string, string> = {
  in_use: '使用中',
  idle: '闲置',
  maintenance: '维护中',
  retired: '已退役',
  scrapped: '已报废'
}

const statusColorMap: Record<string, string> = {
  in_use: '#67c23a',
  idle: '#909399',
  maintenance: '#e6a23c',
  retired: '#f56c6c',
  scrapped: '#c0c4cc'
}

function statusLabel(status: string) {
  return statusMap[status] || status
}

function statusColor(status: string) {
  return statusColorMap[status] || '#409eff'
}

function statusTagType(status: string) {
  const map: Record<string, any> = {
    in_use: 'success',
    idle: 'info',
    maintenance: 'warning',
    retired: 'danger',
    scrapped: 'info'
  }
  return map[status] || 'info'
}

function formatDate(date: string) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

function getPercentage(count: number) {
  if (!stats.value.totalAssets) return 0
  return Math.round((count / stats.value.totalAssets) * 100)
}

async function fetchStats() {
  try {
    const response = await dashboardApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.charts-row,
.recent-row {
  margin-bottom: 20px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-name {
  width: 80px;
  color: #606266;
}

.status-item .el-progress {
  flex: 1;
}

.status-count {
  width: 50px;
  text-align: right;
  color: #303133;
  font-weight: 500;
}
</style>
