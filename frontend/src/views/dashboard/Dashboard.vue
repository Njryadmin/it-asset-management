<template>
  <div class="dashboard">

    <!-- ── Greeting row ── -->
    <div class="greeting anim-fade-in-up">
      <div class="greeting-text">
        <h1 class="greeting-title">欢迎回来 👋</h1>
        <p class="greeting-sub">以下是你的资产概况，总览全局，运筹帷幄。</p>
      </div>
      <div class="greeting-time">
        <span class="time-label">{{ currentDate }}</span>
      </div>
    </div>

    <!-- ── Stat cards ── -->
    <el-row :gutter="20" class="stats-row anim-stagger">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--blue" @click="$router.push('/assets')">
          <div class="stat-card__icon">
            <el-icon><Box /></el-icon>
          </div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalAssets || 0 }}</div>
            <div class="stat-card__label">资产总数</div>
            <div class="stat-card__sub">涵盖所有分类与状态</div>
          </div>
          <div class="stat-card__arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--green" @click="$router.push('/categories')">
          <div class="stat-card__icon">
            <el-icon><Grid /></el-icon>
          </div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalCategories || 0 }}</div>
            <div class="stat-card__label">资产分类</div>
            <div class="stat-card__sub">已建立的分类体系</div>
          </div>
          <div class="stat-card__arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--orange" @click="$router.push('/suppliers')">
          <div class="stat-card__icon">
            <el-icon><Shop /></el-icon>
          </div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalSuppliers || 0 }}</div>
            <div class="stat-card__label">供应商</div>
            <div class="stat-card__sub">合作供应商数量</div>
          </div>
          <div class="stat-card__arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card stat-card--red" @click="$router.push('/purchases')">
          <div class="stat-card__icon">
            <el-icon><ShoppingCart /></el-icon>
          </div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalPurchaseRequests || 0 }}</div>
            <div class="stat-card__label">采购申请</div>
            <div class="stat-card__sub">全部采购申请记录</div>
          </div>
          <div class="stat-card__arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- ── Charts row ── -->
    <el-row :gutter="20" class="charts-row">

      <!-- Donut chart + legend -->
      <el-col :xs="24" :md="12">
        <div class="panel panel--chart">
          <div class="panel__header">
            <span class="panel__title">资产状态分布</span>
            <el-tag size="small" type="info" effect="plain">总计 {{ stats.totalAssets || 0 }}</el-tag>
          </div>
          <div class="panel__body donut-layout">
            <!-- CSS donut chart -->
            <div
              class="donut-chart"
              :style="donutStyle"
            >
              <div class="donut-center">
                <span class="donut-center__num">{{ stats.totalAssets || 0 }}</span>
                <span class="donut-center__txt">资产</span>
              </div>
            </div>
            <!-- Legend -->
            <div class="donut-legend">
              <div
                v-for="(item, i) in statusLegendItems"
                :key="item.key"
                class="legend-item"
                :style="{ animationDelay: `${i * 60}ms` }"
              >
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <span class="legend-label">{{ item.label }}</span>
                <span class="legend-count">{{ item.count }}</span>
                <span class="legend-pct">{{ item.pct }}%</span>
              </div>
              <el-empty
                v-if="!hasStatusData"
                description="暂无数据"
                :image-size="60"
              />
            </div>
          </div>
        </div>
      </el-col>

      <!-- Pending purchase requests -->
      <el-col :xs="24" :md="12">
        <div class="panel">
          <div class="panel__header">
            <span class="panel__title">待审批采购申请</span>
            <el-badge
              v-if="stats.pendingPurchaseRequests?.length"
              :value="stats.pendingPurchaseRequests.length"
              :max="99"
              class="badge-dot"
            />
            <el-button
              v-if="stats.pendingPurchaseRequests?.length"
              size="small"
              type="primary"
              plain
              @click="$router.push('/purchases')"
            >
              查看全部
            </el-button>
          </div>
          <div class="panel__body">
            <div v-if="stats.pendingPurchaseRequests?.length" class="purchase-list">
              <div
                v-for="(req, i) in stats.pendingPurchaseRequests.slice(0, 6)"
                :key="req.id"
                class="purchase-item anim-fade-in-up"
                :style="{ animationDelay: `${i * 60}ms` }"
              >
                <div class="purchase-item__left">
                  <div class="purchase-item__icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="purchase-item__info">
                    <span class="purchase-item__title">{{ req.title }}</span>
                    <span class="purchase-item__meta">
                      数量 × {{ req.quantity }}
                      <span v-if="req.estimatedPrice"> · ¥{{ req.estimatedPrice.toLocaleString() }}</span>
                    </span>
                  </div>
                </div>
                <div class="purchase-item__right">
                  <el-tag size="small" type="warning" effect="light">待审批</el-tag>
                  <span class="purchase-item__date">{{ formatDateShort(req.createdAt) }}</span>
                </div>
              </div>
            </div>
            <el-empty
              v-else
              description="暂无待审批申请"
              :image-size="60"
            >
              <template #image>
                <el-icon :size="48" color="#dcdfe6"><Document /></el-icon>
              </template>
            </el-empty>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- ── Recent assets ── -->
    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <div class="panel">
          <div class="panel__header">
            <span class="panel__title">最近添加的资产</span>
            <el-button size="small" type="primary" plain @click="$router.push('/assets')">
              资产管理
            </el-button>
          </div>
          <div class="panel__body">
            <el-table
              v-if="stats.recentAssets?.length"
              :data="stats.recentAssets"
              style="width: 100%"
              :header-cell-style="{ background: 'var(--theme-border-light)', color: 'var(--theme-text-secondary)', fontWeight: '600' }"
              :row-class-name="'table-row'"
              class="recent-table"
            >
              <el-table-column prop="name" label="资产名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="assetCode" label="资产编号" width="160">
                <template #default="{ row }">
                  <span class="asset-code">{{ row.assetCode || '—' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag size="small" :type="statusTagType(row.status)" effect="light" round>
                    {{ statusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="purchasePrice" label="购买价格" width="120">
                <template #default="{ row }">
                  <span class="price-text">{{ row.purchasePrice ? `¥${Number(row.purchasePrice).toLocaleString()}` : '—' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="categoryId" label="分类" width="120">
                <template #default="{ row }">
                  <span class="category-text">{{ getCategoryName(row.categoryId) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="添加时间" width="160">
                <template #default="{ row }">
                  <span class="date-text">{{ formatDate(row.createdAt) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="$router.push(`/assets/${row.id}/edit`)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty
              v-else
              description="暂无资产记录"
              :image-size="60"
            >
              <el-button type="primary" @click="$router.push('/assets/create')">
                立即添加
              </el-button>
            </el-empty>
          </div>
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import type { DashboardStats } from '@/types'
import { useAssetStore } from '@/stores/assets'
import dayjs from 'dayjs'

const assetStore = useAssetStore()

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

const currentDate = computed(() => dayjs().format('YYYY年MM月DD日 dddd'))

const statusColorMap: Record<string, string> = {
  in_use:      '#67c23a',
  idle:        '#909399',
  maintenance: '#e6a23c',
  retired:     '#f56c6c',
  scrapped:    '#c0c4cc'
}

const statusLabelMap: Record<string, string> = {
  in_use:      '使用中',
  idle:        '闲置',
  maintenance: '维护中',
  retired:     '已退役',
  scrapped:    '已报废'
}

function statusLabel(status: string) {
  return statusLabelMap[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    in_use:      'success',
    idle:        'info',
    maintenance: 'warning',
    retired:     'danger',
    scrapped:    'info'
  }
  return map[status] || 'info'
}

function formatDate(date: string | null | undefined) {
  if (!date) return '—'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

function formatDateShort(date: string | null | undefined) {
  if (!date) return '—'
  return dayjs(date).format('MM/DD HH:mm')
}

function getCategoryName(id: number | null) {
  if (!id) return '—'
  const cat = flatCategories.value.find((c: any) => c.id === id)
  return cat?.name || '—'
}

const flatCategories = computed(() => {
  const result: any[] = []
  function flatten(cats: any[], level = 0) {
    for (const cat of cats) {
      result.push({ ...cat, level })
      if (cat.children?.length) flatten(cat.children, level + 1)
    }
  }
  flatten(assetStore.categories)
  return result
})

const statusOrder = ['in_use', 'idle', 'maintenance', 'retired', 'scrapped']

const hasStatusData = computed(() => {
  return Object.values(stats.value.assetsByStatus || {}).some((v: any) => v > 0)
})

// Build CSS donut chart style from asset status data
const donutStyle = computed(() => {
  const total = stats.value.totalAssets || 0
  if (!total) return {}

  const colors: Record<string, string> = {
    in_use:      '#67c23a',
    idle:        '#909399',
    maintenance: '#e6a23c',
    retired:     '#f56c6c',
    scrapped:    '#c0c4cc'
  }

  let startDeg = 0
  const segments: string[] = []
  const angles: Record<string, string> = {}

  for (const key of statusOrder) {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    if (!count) { angles[key] = '0deg'; continue }
    const deg = (count / total) * 360
    angles[key] = `${startDeg}deg`
    segments.push(`${colors[key]} ${startDeg}deg ${startDeg + deg}deg`)
    startDeg += deg
  }

  // Build conic-gradient string
  const gradientParts: string[] = []
  let currentDeg = 0
  for (const key of statusOrder) {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    if (!count) continue
    const deg = (count / total) * 360
    gradientParts.push(`${colors[key]} ${currentDeg}deg ${currentDeg + deg}deg`)
    currentDeg += deg
  }
  // Fill remaining with a light gray
  if (currentDeg < 360) {
    gradientParts.push(`#e4e7ed ${currentDeg}deg 360deg`)
  }

  return {
    background: `conic-gradient(${gradientParts.join(', ')})`,
  }
})

interface LegendItem {
  key: string
  label: string
  color: string
  count: number
  pct: string
}

const statusLegendItems = computed<LegendItem[]>(() => {
  const total = stats.value.totalAssets || 0
  return statusOrder
    .map(key => {
      const count = (stats.value.assetsByStatus as any)?.[key] || 0
      return {
        key,
        label: statusLabelMap[key] || key,
        color: statusColorMap[key] || '#909399',
        count,
        pct: total ? ((count / total) * 100).toFixed(1) : '0',
      }
    })
    .filter(item => item.count > 0)
})

async function fetchStats() {
  try {
    const response = await dashboardApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStats(),
    assetStore.fetchOptions().catch(() => {}),
  ])
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding-bottom: 24px;
}

/* ── Greeting ── */
.greeting {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: var(--theme-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--theme-shadow);
  border: 1px solid var(--theme-border-light);
}

.greeting-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--theme-text-primary);
  margin-bottom: 4px;
}

.greeting-sub {
  font-size: 14px;
  color: var(--theme-text-secondary);
}

.greeting-time {
  text-align: right;
}

.time-label {
  font-size: 13px;
  color: var(--theme-text-placeholder);
  padding: 4px 12px;
  background: var(--theme-border-light);
  border-radius: 20px;
}

/* ── Stat cards ── */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  margin-bottom: 12px;
}

.stat-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.06;
  background: linear-gradient(135deg, #fff 0%, transparent 60%);
  pointer-events: none;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
}

.stat-card--blue {
  background: linear-gradient(135deg, var(--theme-primary, #409eff) 0%, var(--theme-primary-light, #66b3ff) 100%);
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.35);
  color: #fff;
}
.stat-card--green {
  background: linear-gradient(135deg, var(--theme-success, #67c23a) 0%, var(--theme-success-light, #85ce61) 100%);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.35);
  color: #fff;
}
.stat-card--orange {
  background: linear-gradient(135deg, var(--theme-warning, #e6a23c) 0%, var(--theme-warning-light, #ebb563) 100%);
  box-shadow: 0 4px 16px rgba(230, 162, 60, 0.35);
  color: #fff;
}
.stat-card--red {
  background: linear-gradient(135deg, var(--theme-danger, #f56c6c) 0%, var(--theme-danger-light, #f78989) 100%);
  box-shadow: 0 4px 16px rgba(245, 108, 108, 0.35);
  color: #fff;
}

.stat-card__icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
}

.stat-card__body {
  flex: 1;
  min-width: 0;
}

.stat-card__value {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.1;
  color: #fff;
  letter-spacing: -1px;
}

.stat-card__label {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
  margin-top: 2px;
}

.stat-card__sub {
  font-size: 12px;
  color: rgba(255,255,255,0.65);
  margin-top: 2px;
}

.stat-card__arrow {
  font-size: 18px;
  color: rgba(255,255,255,0.6);
  flex-shrink: 0;
  transition: transform var(--transition-fast), color var(--transition-fast);
}

.stat-card:hover .stat-card__arrow {
  transform: translateX(4px);
  color: #fff;
}

/* ── Panel (chart / table cards) ── */
.panel {
  background: var(--theme-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--theme-shadow);
  border: 1px solid var(--theme-border-light);
  overflow: hidden;
  margin-bottom: 20px;
  transition: box-shadow var(--transition-normal);
}

.panel:hover {
  box-shadow: var(--theme-shadow-hover);
}

.panel__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--theme-border-light);
}

.panel__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--theme-text-primary);
  flex: 1;
}

.panel__body {
  padding: 20px;
}

/* ── Donut chart ── */
.donut-layout {
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}

.donut-chart {
  position: relative;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: background var(--transition-slow);
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--theme-card);
  margin: 20px;
}

.donut-center__num {
  font-size: 28px;
  font-weight: 800;
  color: var(--theme-text-primary);
  line-height: 1;
}

.donut-center__txt {
  font-size: 12px;
  color: var(--theme-text-secondary);
  margin-top: 2px;
}

.donut-legend {
  flex: 1;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
  animation: fadeInUp 0.3s ease both;
}

.legend-item:hover {
  background: var(--theme-border-light);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 13px;
  color: var(--theme-text-secondary);
}

.legend-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--theme-text-primary);
  min-width: 36px;
  text-align: right;
}

.legend-pct {
  font-size: 12px;
  color: var(--theme-text-placeholder);
  min-width: 42px;
  text-align: right;
}

/* ── Purchase list ── */
.purchase-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.purchase-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
  gap: 12px;
}

.purchase-item:hover {
  background: var(--theme-border-light);
}

.purchase-item__left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.purchase-item__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--theme-warning-bg, #fff7e6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-warning, #e6a23c);
  font-size: 18px;
  flex-shrink: 0;
}

.purchase-item__info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.purchase-item__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--theme-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.purchase-item__meta {
  font-size: 12px;
  color: var(--theme-text-secondary);
  margin-top: 1px;
}

.purchase-item__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.purchase-item__date {
  font-size: 11px;
  color: var(--theme-text-placeholder);
}

/* ── Recent assets table ── */
.recent-table {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.asset-code {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 12px;
  color: var(--theme-primary);
  background: var(--theme-border-light);
  padding: 2px 6px;
  border-radius: 4px;
}

.price-text {
  font-weight: 600;
  color: var(--theme-text-primary);
}

.category-text {
  color: var(--theme-text-secondary);
  font-size: 13px;
}

.date-text {
  color: var(--theme-text-secondary);
  font-size: 13px;
}

/* Badge dot */
.badge-dot {
  margin-top: 2px;
}

/* Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 768px) {
  .greeting {
    flex-direction: column;
    gap: 12px;
  }
  .greeting-time {
    text-align: left;
  }
  .donut-layout {
    flex-direction: column;
    align-items: flex-start;
  }
  .donut-legend {
    width: 100%;
  }
  .purchase-item__right .el-tag {
    display: none;
  }
}
</style>
