<template>
  <div class="dashboard">

    <!-- ══ Brand Header ══ -->
    <div class="brand-header anim-fade-in-up">
      <div class="brand-header__left">
        <div v-if="settings.logoUrl" class="brand-header__logo">
          <img :src="settings.logoUrl" :alt="settings.systemName" />
        </div>
        <div v-else class="brand-header__icon">💻</div>
        <div class="brand-header__info">
          <div class="brand-header__name">{{ settings.systemName || 'IT 资产管理系统' }}</div>
          <div class="brand-header__sub">{{ greetingText }} · {{ currentWeekday }}</div>
        </div>
      </div>
      <div class="brand-header__right">
        <div class="brand-header__date">{{ currentDate }}</div>
        <div class="brand-header__time">{{ currentTime }}</div>
      </div>
    </div>

    <!-- ══ Stat Cards Grid ══ -->
    <el-row :gutter="12" class="stats-grid anim-stagger">
      <!-- 资产总数 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--green" @click="$router.push('/assets')">
          <div class="stat-card__icon"><el-icon><Box /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalAssets || 0 }}</div>
            <div class="stat-card__label">资产总数</div>
          </div>
        </div>
      </el-col>

      <!-- 资产分类 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--blue" @click="$router.push('/categories')">
          <div class="stat-card__icon"><el-icon><Grid /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalCategories || 0 }}</div>
            <div class="stat-card__label">资产分类</div>
          </div>
        </div>
      </el-col>

      <!-- 供应商 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--orange" @click="$router.push('/suppliers')">
          <div class="stat-card__icon"><el-icon><Shop /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalSuppliers || 0 }}</div>
            <div class="stat-card__label">供应商</div>
          </div>
        </div>
      </el-col>

      <!-- 部门 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--purple" @click="$router.push('/departments')">
          <div class="stat-card__icon"><el-icon><OfficeBuilding /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalDepartments || 0 }}</div>
            <div class="stat-card__label">部门</div>
          </div>
        </div>
      </el-col>

      <!-- 今日入库 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--cyan">
          <div class="stat-card__icon"><el-icon><Bottom /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ todayInCount }}</div>
            <div class="stat-card__label">今日入库</div>
          </div>
        </div>
      </el-col>

      <!-- 今日出库 -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--red">
          <div class="stat-card__icon"><el-icon><Top /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ todayOutCount }}</div>
            <div class="stat-card__label">今日出库</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- ══ Main Content Row ══ -->
    <el-row :gutter="12" class="content-row">

      <!-- ── Left Column ── -->
      <el-col :xs="24" :md="14">

        <!-- Asset Status Donut -->
        <div class="panel anim-fade-in-up" style="animation-delay:100ms">
          <div class="panel__header">
            <span class="panel__title">资产状态分布</span>
            <span class="panel__badge">共 {{ stats.totalAssets || 0 }} 项</span>
          </div>
          <div class="panel__body donut-layout">
            <div class="donut-wrap">
              <div class="donut-chart" :style="donutStyle">
                <div class="donut-center">
                  <span class="donut-center__num">{{ stats.totalAssets || 0 }}</span>
                  <span class="donut-center__txt">资产</span>
                </div>
              </div>
            </div>
            <div class="donut-legend">
              <div
                v-for="item in statusLegendItems"
                :key="item.key"
                class="legend-item"
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

        <!-- Asset Usage Rate Progress -->
        <div class="panel anim-fade-in-up" style="animation-delay:160ms">
          <div class="panel__header">
            <span class="panel__title">资产使用率</span>
          </div>
          <div class="panel__body usage-rates">
            <div class="usage-rate-item">
              <div class="usage-rate-item__label">
                <span>使用中</span>
                <span class="usage-rate-item__count">
                  {{ stats.assetsByStatus?.inUse || 0 }} / {{ stats.totalAssets || 0 }}
                </span>
              </div>
              <el-progress
                :percentage="usageRate('inUse')"
                :stroke-width="10"
                :color="statusColorMap.inUse"
                :show-text="true"
              />
            </div>
            <div class="usage-rate-item">
              <div class="usage-rate-item__label">
                <span>闲置中</span>
                <span class="usage-rate-item__count">
                  {{ stats.assetsByStatus?.idle || 0 }} / {{ stats.totalAssets || 0 }}
                </span>
              </div>
              <el-progress
                :percentage="usageRate('idle')"
                :stroke-width="10"
                :color="statusColorMap.idle"
                :show-text="true"
              />
            </div>
            <div class="usage-rate-item">
              <div class="usage-rate-item__label">
                <span>维护中</span>
                <span class="usage-rate-item__count">
                  {{ stats.assetsByStatus?.maintenance || 0 }} / {{ stats.totalAssets || 0 }}
                </span>
              </div>
              <el-progress
                :percentage="usageRate('maintenance')"
                :stroke-width="10"
                :color="statusColorMap.maintenance"
                :show-text="true"
              />
            </div>
          </div>
        </div>

        <!-- Recent Assets -->
        <div class="panel anim-fade-in-up" style="animation-delay:220ms">
          <div class="panel__header">
            <span class="panel__title">最近添加的资产</span>
            <el-button size="small" type="primary" plain @click="$router.push('/assets')">
              资产管理
            </el-button>
          </div>
          <div class="panel__body" style="padding:0">
            <el-table
              v-if="stats.recentAssets?.length"
              :data="stats.recentAssets"
              style="width:100%"
              class="recent-table"
            >
              <el-table-column prop="name" label="资产名称" min-width="140" show-overflow-tooltip />
              <el-table-column prop="assetCode" label="编号" width="130">
                <template #default="{ row }">
                  <span class="asset-code">{{ row.assetCode || '—' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="90">
                <template #default="{ row }">
                  <el-tag size="small" :type="statusTagType(row.status)" effect="light">
                    {{ statusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="purchasePrice" label="价格" width="110">
                <template #default="{ row }">
                  <span class="price-text">
                    {{ row.purchasePrice ? `¥${Number(row.purchasePrice).toLocaleString()}` : '—' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="添加时间" width="150">
                <template #default="{ row }">
                  <span class="date-text">{{ formatDate(row.createdAt) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="90" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="$router.push(`/assets/${row.id}/edit`)">
                    详情
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

      <!-- ── Right Column ── -->
      <el-col :xs="24" :md="10">

        <!-- Pending Purchases -->
        <div class="panel anim-fade-in-up" style="animation-delay:130ms">
          <div class="panel__header">
            <span class="panel__title">待审批采购</span>
            <span v-if="stats.pendingPurchaseRequests?.length" class="panel__badge panel__badge--danger">
              {{ stats.pendingPurchaseRequests.length }}
            </span>
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
                v-for="req in stats.pendingPurchaseRequests.slice(0, 8)"
                :key="req.id"
                class="purchase-item"
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
                <el-icon :size="48" color="#E5E5E5"><Document /></el-icon>
              </template>
            </el-empty>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="panel anim-fade-in-up" style="animation-delay:190ms">
          <div class="panel__header">
            <span class="panel__title">快捷操作</span>
          </div>
          <div class="panel__body">
            <div class="quick-actions">
              <div class="quick-action" @click="$router.push('/assets/create')">
                <div class="quick-action__icon quick-action__icon--green">
                  <el-icon><Plus /></el-icon>
                </div>
                <span class="quick-action__label">添加资产</span>
              </div>
              <div class="quick-action" @click="$router.push('/purchases')">
                <div class="quick-action__icon quick-action__icon--orange">
                  <el-icon><ShoppingCart /></el-icon>
                </div>
                <span class="quick-action__label">采购申请</span>
              </div>
              <div class="quick-action" @click="$router.push('/categories')">
                <div class="quick-action__icon quick-action__icon--blue">
                  <el-icon><Grid /></el-icon>
                </div>
                <span class="quick-action__label">资产分类</span>
              </div>
              <div class="quick-action" @click="$router.push('/suppliers')">
                <div class="quick-action__icon quick-action__icon--purple">
                  <el-icon><Shop /></el-icon>
                </div>
                <span class="quick-action__label">供应商</span>
              </div>
            </div>
          </div>
        </div>

        <!-- System Summary -->
        <div class="panel anim-fade-in-up" style="animation-delay:250ms">
          <div class="panel__header">
            <span class="panel__title">系统概览</span>
          </div>
          <div class="panel__body">
            <div class="summary-list">
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--green">📦</span>
                <span class="summary-item__label">资产总数</span>
                <span class="summary-item__value">{{ stats.totalAssets || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--blue">🏷️</span>
                <span class="summary-item__label">分类数</span>
                <span class="summary-item__value">{{ stats.totalCategories || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--orange">🏪</span>
                <span class="summary-item__label">供应商</span>
                <span class="summary-item__value">{{ stats.totalSuppliers || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--purple">🏢</span>
                <span class="summary-item__label">部门</span>
                <span class="summary-item__value">{{ stats.totalDepartments || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--cyan">👤</span>
                <span class="summary-item__label">用户</span>
                <span class="summary-item__value">{{ stats.totalUsers || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon summary-item__icon--red">📋</span>
                <span class="summary-item__label">采购申请</span>
                <span class="summary-item__value">{{ stats.totalPurchaseRequests || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

      </el-col>
    </el-row>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import { settingsApi } from '@/api/settings'
import type { DashboardStats } from '@/types'
import { useAssetStore } from '@/stores/assets'
import dayjs from 'dayjs'

const assetStore = useAssetStore()

// ── Settings ──
const settings = ref({
  systemName: 'IT 资产管理系统',
  logoUrl: '',
})

// ── Dashboard Stats ──
const stats = ref<DashboardStats & { todayIn?: number; todayOut?: number }>({
  totalAssets: 0,
  totalCategories: 0,
  totalSuppliers: 0,
  totalDepartments: 0,
  totalUsers: 0,
  totalPurchaseRequests: 0,
  assetsByStatus: {},
  assetsByCategory: {},
  recentAssets: [],
  pendingPurchaseRequests: [],
})

// ── Time ──
const currentTime = ref(dayjs().format('HH:mm'))
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))
const currentWeekday = computed(() => ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][dayjs().day()])
const greetingText = computed(() => {
  const h = dayjs().hour()
  if (h < 5) return '凌晨好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

let timeTimer: ReturnType<typeof setInterval>

onMounted(() => {
  timeTimer = setInterval(() => {
    currentTime.value = dayjs().format('HH:mm')
  }, 60000)
})

onUnmounted(() => {
  clearInterval(timeTimer)
})

// ── Today counts (from recent assets as proxy if not available) ──
const todayInCount = computed(() => {
  const s = stats.value as any
  if (s.todayIn !== undefined) return s.todayIn
  const today = dayjs().format('YYYY-MM-DD')
  return (stats.value.recentAssets || []).filter((a: any) =>
    a.purchaseDate === today || (a.createdAt && dayjs(a.createdAt).format('YYYY-MM-DD') === today)
  ).length
})

const todayOutCount = computed(() => {
  const s = stats.value as any
  if (s.todayOut !== undefined) return s.todayOut
  return 0
})

// ── Status ──
const statusColorMap: Record<string, string> = {
  inUse:      '#1AAD19',
  idle:        '#909399',
  maintenance: '#FF991A',
  retired:     '#FA5151',
  scrapped:    '#C0C4CC',
}

const statusLabelMap: Record<string, string> = {
  inUse:      '使用中',
  idle:        '闲置',
  maintenance: '维护中',
  retired:     '已退役',
  scrapped:    '已报废',
}

const statusOrder = ['inUse', 'idle', 'maintenance', 'retired', 'scrapped']

function statusLabel(status: string) {
  return statusLabelMap[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    inUse:      'success',
    idle:        'info',
    maintenance: 'warning',
    retired:     'danger',
    scrapped:    'info',
  }
  return map[status] || 'info'
}

function usageRate(key: string) {
  const total = stats.value.totalAssets || 0
  if (!total) return 0
  return Math.round(((stats.value.assetsByStatus as any)?.[key] || 0) / total * 100)
}

function formatDate(date: string | null | undefined) {
  if (!date) return '—'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

function formatDateShort(date: string | null | undefined) {
  if (!date) return '—'
  return dayjs(date).format('MM/DD HH:mm')
}

const hasStatusData = computed(() => {
  return Object.values(stats.value.assetsByStatus || {}).some((v: any) => v > 0)
})

// ── Donut Chart ──
const donutStyle = computed(() => {
  const total = stats.value.totalAssets || 0
  if (!total) return {}

  const gradientParts: string[] = []
  let currentDeg = 0

  for (const key of statusOrder) {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    if (!count) continue
    const deg = (count / total) * 360
    gradientParts.push(`${statusColorMap[key] || '#909399'} ${currentDeg}deg ${currentDeg + deg}deg`)
    currentDeg += deg
  }
  if (currentDeg < 360) {
    gradientParts.push(`#F0F0F0 ${currentDeg}deg 360deg`)
  }

  return { background: `conic-gradient(${gradientParts.join(', ')})` }
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
})

// ── Fetch Data ──
async function fetchStats() {
  try {
    const response = await dashboardApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

async function fetchSettings() {
  try {
    const response = await settingsApi.get()
    if (response.data) {
      settings.value.systemName = (response.data as any).systemName || (response.data as any).siteTitle || 'IT 资产管理系统'
      settings.value.logoUrl = (response.data as any).logoUrl || ''
    }
  } catch (error) {
    console.error('Failed to fetch settings:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    fetchStats(),
    fetchSettings().catch(() => {}),
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

/* ── Brand Header ── */
.brand-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 22px;
  margin-bottom: 14px;
  background: var(--wechat-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--wechat-shadow-card);
  border: 1px solid var(--wechat-border-light);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  position: relative;
  overflow: hidden;
}

.brand-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 220px;
  height: 100%;
  background: linear-gradient(135deg, rgba(26, 173, 25, 0.08) 0%, rgba(26, 173, 25, 0.03) 100%);
  pointer-events: none;
}

.brand-header__left {
  display: flex;
  align-items: center;
  gap: 14px;
  position: relative;
}

.brand-header__logo img {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  object-fit: contain;
  background: var(--wechat-bg);
  padding: 4px;
}

.brand-header__icon {
  font-size: 36px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-header__name {
  font-size: 18px;
  font-weight: 700;
  color: var(--wechat-text);
  line-height: 1.3;
}

.brand-header__sub {
  font-size: 13px;
  color: var(--wechat-text-secondary);
  margin-top: 2px;
}

.brand-header__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  position: relative;
}

.brand-header__date {
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.brand-header__time {
  font-size: 22px;
  font-weight: 700;
  color: var(--wechat-primary);
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  line-height: 1;
}

/* ── Stat Cards Grid ── */
.stats-grid {
  margin-bottom: 14px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 10px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  margin-bottom: 8px;
  transition: transform 200ms ease, box-shadow 200ms ease;
  position: relative;
  overflow: hidden;
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  transform: translate(30%, -30%);
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card--green  { background: linear-gradient(135deg, #1AAD19 0%, #148D14 100%); box-shadow: 0 4px 14px rgba(26,173,25,0.3); }
.stat-card--blue   { background: linear-gradient(135deg, #409EFF 0%, #337ECC 100%); box-shadow: 0 4px 14px rgba(64,158,255,0.3); }
.stat-card--orange { background: linear-gradient(135deg, #FF991A 0%, #E68A00 100%); box-shadow: 0 4px 14px rgba(255,153,26,0.3); }
.stat-card--purple { background: linear-gradient(135deg, #9C6ADE 0%, #7B52B5 100%); box-shadow: 0 4px 14px rgba(156,106,222,0.3); }
.stat-card--cyan   { background: linear-gradient(135deg, #00BCD4 0%, #0097A7 100%); box-shadow: 0 4px 14px rgba(0,188,212,0.3); }
.stat-card--red     { background: linear-gradient(135deg, #FA5151 0%, #D94444 100%); box-shadow: 0 4px 14px rgba(250,81,81,0.3); }

.stat-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  color: #fff;
}

.stat-card__value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
  letter-spacing: -0.5px;
}

.stat-card__label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  margin-top: 2px;
}

/* ── Panel ── */
.panel {
  background: var(--wechat-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--wechat-shadow-card);
  border: 1px solid var(--wechat-border-light);
  overflow: hidden;
  margin-bottom: 14px;
}

.panel__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 18px;
  border-bottom: 1px solid var(--wechat-border-light);
}

.panel__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--wechat-text);
  flex: 1;
}

.panel__badge {
  font-size: 12px;
  color: var(--wechat-text-secondary);
  background: var(--wechat-bg);
  padding: 2px 10px;
  border-radius: 10px;
}

.panel__badge--danger {
  background: var(--wechat-danger);
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
}

.panel__body {
  padding: 18px;
}

/* ── Donut Chart ── */
.donut-layout {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.donut-wrap {
  flex-shrink: 0;
}

.donut-chart {
  position: relative;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--wechat-card);
  margin: 16px;
}

.donut-center__num {
  font-size: 24px;
  font-weight: 800;
  color: var(--wechat-text);
  line-height: 1;
}

.donut-center__txt {
  font-size: 11px;
  color: var(--wechat-text-secondary);
  margin-top: 2px;
}

.donut-legend {
  flex: 1;
  min-width: 140px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.legend-item:hover {
  background: var(--wechat-bg);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.legend-count {
  font-size: 13px;
  font-weight: 600;
  color: var(--wechat-text);
  min-width: 28px;
  text-align: right;
}

.legend-pct {
  font-size: 11px;
  color: var(--wechat-text-placeholder);
  min-width: 36px;
  text-align: right;
}

/* ── Usage Rate Progress ── */
.usage-rates {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.usage-rate-item__label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.usage-rate-item__count {
  font-weight: 600;
  color: var(--wechat-text);
  font-size: 13px;
}

/* ── Purchase List ── */
.purchase-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.purchase-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 9px 8px;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
  gap: 10px;
}

.purchase-item:hover {
  background: var(--wechat-bg);
}

.purchase-item__left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.purchase-item__icon {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--wechat-warning-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--wechat-warning);
  font-size: 17px;
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
  color: var(--wechat-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.purchase-item__meta {
  font-size: 12px;
  color: var(--wechat-text-secondary);
  margin-top: 1px;
}

.purchase-item__right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
  flex-shrink: 0;
}

.purchase-item__date {
  font-size: 11px;
  color: var(--wechat-text-placeholder);
}

/* ── Quick Actions ── */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 14px 8px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast), transform var(--transition-fast);
  background: var(--wechat-bg);
  border: 1px solid var(--wechat-border-light);
}

.quick-action:hover {
  background: var(--wechat-border-light);
  transform: translateY(-2px);
}

.quick-action__icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.quick-action__icon--green  { background:rgba(26, 173, 25, 0.12); color: #1AAD19; }
.quick-action__icon--orange { background: rgba(255, 153, 26, 0.12); color: #FF991A; }
.quick-action__icon--blue   { background: rgba(64, 158, 255, 0.12); color: #409EFF; }
.quick-action__icon--purple { background: rgba(156, 106, 222, 0.12); color: #9C6ADE; }

.quick-action__label {
  font-size: 12px;
  font-weight: 500;
  color: var(--wechat-text-secondary);
  text-align: center;
}

/* ── Summary List ── */
.summary-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 6px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.summary-item:hover {
  background: var(--wechat-bg);
}

.summary-item__icon {
  font-size: 16px;
  width: 28px;
  text-align: center;
  flex-shrink: 0;
}

.summary-item__label {
  flex: 1;
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.summary-item__value {
  font-size: 14px;
  font-weight: 700;
  color: var(--wechat-text);
}

/* ── Recent Table ── */
.asset-code {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 12px;
  color: var(--wechat-primary);
  background: #E8F7E4;
  padding: 2px 6px;
  border-radius: 4px;
}

.price-text {
  font-weight: 600;
  color: var(--wechat-text);
}

.date-text {
  color: var(--wechat-text-secondary);
  font-size: 12px;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .brand-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 16px 18px;
  }
  .brand-header__right {
    align-items: flex-start;
    flex-direction: row;
    gap: 12px;
    align-items: center;
  }
  .brand-header__time {
    font-size: 18px;
  }
  .stats-grid .el-col {
    margin-bottom: 0;
  }
  .stat-card {
    margin-bottom: 0;
  }
  .donut-layout {
    flex-direction: column;
    align-items: flex-start;
  }
  .donut-legend {
    width: 100%;
  }
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  .content-row > .el-col {
    margin-bottom: 0;
  }
  .panel {
    margin-bottom: 12px;
  }
}

@media (max-width: 480px) {
  .stats-grid .el-col {
    padding: 0 4px !important;
  }
  .stat-card {
    padding: 12px 10px;
  }
  .stat-card__value {
    font-size: 20px;
  }
  .stat-card__icon {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
}

</style>
