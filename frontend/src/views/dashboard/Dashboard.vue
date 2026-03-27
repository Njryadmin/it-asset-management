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

        <!-- Asset Status Donut — Redesigned -->
        <div class="panel anim-fade-in-up" style="animation-delay:100ms">
          <div class="panel__header">
            <span class="panel__title">📊 资产状态分布</span>
            <span class="panel__badge">共 {{ stats.totalAssets || 0 }} 项</span>
          </div>
          <div class="panel__body status-dist-grid">
            <!-- Donut Chart -->
            <div class="donut-wrapper">
              <div class="donut-ring">
                <svg viewBox="0 0 200 200" class="donut-svg">
                  <circle
                    v-for="(seg, i) in donutSegments"
                    :key="seg.key"
                    cx="100" cy="100" r="72"
                    fill="none"
                    :stroke="seg.color"
                    stroke-width="22"
                    :stroke-dasharray="seg.dashArray"
                    :stroke-dashoffset="seg.dashOffset"
                    :stroke-linecap="seg.dashArray !== '0 452.39' ? 'butt' : 'butt'"
                    class="donut-seg"
                    :style="{ animationDelay: i * 80 + 'ms' }"
                  />
                </svg>
                <div class="donut-core">
                  <span class="donut-core__pct">{{ overallUsagePct }}%</span>
                  <span class="donut-core__label">使用率</span>
                </div>
              </div>
            </div>
            <!-- Status Cards -->
            <div class="status-cards">
              <div
                v-for="item in statusCardItems"
                :key="item.key"
                class="status-card"
                :style="{ '--status-color': item.color }"
              >
                <div class="status-card__top">
                  <span class="status-card__name">{{ item.label }}</span>
                  <span class="status-card__count" :style="{ color: item.color }">{{ item.count }}</span>
                </div>
                <div class="status-card__bar-track">
                  <div
                    class="status-card__bar-fill"
                    :style="{ width: item.pct + '%', background: item.color }"
                  ></div>
                </div>
                <div class="status-card__bottom">
                  <span class="status-card__pct">{{ item.pct }}%</span>
                  <span class="status-card__pct-label">占比</span>
                </div>
              </div>
              <el-empty v-if="!hasStatusData" description="暂无数据" :image-size="60" />
            </div>
          </div>
        </div>

        <!-- Asset Usage Rate — Redesigned -->
        <div class="panel anim-fade-in-up" style="animation-delay:160ms">
          <div class="panel__header">
            <span class="panel__title">📈 资产使用率</span>
            <span class="panel__badge panel__badge--green">整体 {{ overallUsagePct }}%</span>
          </div>
          <div class="panel__body usage-section">
            <!-- Usage Gauge -->
            <div class="usage-gauge-wrap">
              <div class="usage-gauge">
                <svg viewBox="0 0 120 120" class="gauge-svg">
                  <circle
                    cx="60" cy="60" r="50"
                    fill="none"
                    stroke="var(--wechat-bg)"
                    stroke-width="10"
                  />
                  <circle
                    cx="60" cy="60" r="50"
                    fill="none"
                    :stroke="usageGaugeColor"
                    stroke-width="10"
                    stroke-linecap="round"
                    :stroke-dasharray="gaugeDashArray"
                    stroke-dashoffset="0"
                    transform="rotate(-90 60 60)"
                    class="gauge-fill"
                  />
                </svg>
                <div class="gauge-label">
                  <span class="gauge-label__pct" :style="{ color: usageGaugeColor }">{{ overallUsagePct }}%</span>
                  <span class="gauge-label__txt">使用率</span>
                </div>
              </div>
              <div class="usage-summary">
                <div class="usage-summary__item">
                  <span class="usage-summary__num" style="color:#1AAD19">{{ stats.assetsByStatus?.inUse || 0 }}</span>
                  <span class="usage-summary__desc">在用资产</span>
                </div>
                <div class="usage-summary__divider"></div>
                <div class="usage-summary__item">
                  <span class="usage-summary__num" style="color:#909399">{{ stats.assetsByStatus?.idle || 0 }}</span>
                  <span class="usage-summary__desc">闲置资产</span>
                </div>
                <div class="usage-summary__divider"></div>
                <div class="usage-summary__item">
                  <span class="usage-summary__num" style="color:#FF991A">{{ stats.assetsByStatus?.maintenance || 0 }}</span>
                  <span class="usage-summary__desc">维护中</span>
                </div>
              </div>
            </div>
            <!-- Animated Rate Bars -->
            <div class="rate-bars">
              <div v-for="bar in usageBarItems" :key="bar.key" class="rate-bar-item">
                <div class="rate-bar-item__header">
                  <div class="rate-bar-item__info">
                    <span class="rate-bar-dot" :style="{ background: bar.color }"></span>
                    <span class="rate-bar-item__name">{{ bar.label }}</span>
                  </div>
                  <div class="rate-bar-item__nums">
                    <span class="rate-bar-item__count" :style="{ color: bar.color }">{{ bar.count }}</span>
                    <span class="rate-bar-item__total">/ {{ stats.totalAssets || 0 }}</span>
                  </div>
                </div>
                <div class="rate-bar-track">
                  <div
                    class="rate-bar-fill"
                    :class="{ 'rate-bar-fill--animated': bar.count > 0 }"
                    :style="{
                      width: bar.pct + '%',
                      background: `linear-gradient(90deg, ${bar.color}99, ${bar.color})`
                    }"
                  ></div>
                </div>
              </div>
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

// ── SVG Donut Chart ──
const CIRCUMFERENCE = 2 * Math.PI * 72  // ≈ 452.39

interface DonutSeg {
  key: string
  color: string
  dashArray: string
  dashOffset: string
}

const donutSegments = computed<DonutSeg[]>(() => {
  const total = stats.value.totalAssets || 0
  if (!total) return []

  const segments: DonutSeg[] = []
  let accumulated = 0

  for (const key of statusOrder) {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    if (!count) continue

    const pct = count / total
    const arcLen = pct * CIRCUMFERENCE
    const gapLen = CIRCUMFERENCE - arcLen

    segments.push({
      key,
      color: statusColorMap[key] || '#909399',
      dashArray: `${arcLen.toFixed(2)} ${gapLen.toFixed(2)}`,
      dashOffset: (-accumulated * CIRCUMFERENCE).toFixed(2),
    })
    accumulated += pct
  }

  return segments
})

interface StatusCardItem {
  key: string
  label: string
  color: string
  count: number
  pct: number
}

const statusCardItems = computed<StatusCardItem[]>(() => {
  const total = stats.value.totalAssets || 0
  return statusOrder.map(key => {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    return {
      key,
      label: statusLabelMap[key] || key,
      color: statusColorMap[key] || '#909399',
      count,
      pct: total ? Math.round((count / total) * 100) : 0,
    }
  })
})

// ── Usage Rate ──
const overallUsagePct = computed(() => {
  const total = stats.value.totalAssets || 0
  if (!total) return 0
  const inUse = (stats.value.assetsByStatus as any)?.inUse || 0
  return Math.round((inUse / total) * 100)
})

const usageGaugeColor = computed(() => {
  const pct = overallUsagePct.value
  if (pct >= 70) return '#1AAD19'
  if (pct >= 40) return '#FF991A'
  return '#909399'
})

const gaugeDashArray = computed(() => {
  const pct = overallUsagePct.value / 100
  const filled = pct * (2 * Math.PI * 50)
  const total = 2 * Math.PI * 50
  return `${filled.toFixed(2)} ${(total - filled).toFixed(2)}`
})

interface UsageBarItem {
  key: string
  label: string
  color: string
  count: number
  pct: number
}

const usageBarItems = computed<UsageBarItem[]>(() => {
  const total = stats.value.totalAssets || 0
  const keys = ['inUse', 'idle', 'maintenance']
  return keys.map(key => {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    return {
      key,
      label: statusLabelMap[key] || key,
      color: statusColorMap[key] || '#909399',
      count,
      pct: total ? Math.round((count / total) * 100) : 0,
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
      settings.value.systemName = (response.data as any).system_name || (response.data as any).siteTitle || 'IT 资产管理系统'
      settings.value.logoUrl = (response.data as any).logo_url || ''
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

/* ── Status Distribution Grid ── */
.status-dist-grid {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 20px;
  align-items: center;
}

@media (max-width: 600px) {
  .status-dist-grid {
    grid-template-columns: 1fr;
  }
}

/* Donut Ring */
.donut-wrapper {
  display: flex;
  justify-content: center;
}

.donut-ring {
  position: relative;
  width: 160px;
  height: 160px;
  flex-shrink: 0;
}

.donut-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 2px 8px rgba(0,0,0,0.06));
}

.donut-seg {
  transform-origin: center;
  animation: donut-reveal 0.8s cubic-bezier(0.4, 0, 0.2, 1) both;
}

@keyframes donut-reveal {
  from {
    stroke-dasharray: 0 452.39;
    opacity: 0.4;
  }
  to {
    opacity: 1;
  }
}

.donut-core {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.donut-core__pct {
  font-size: 26px;
  font-weight: 800;
  color: var(--wechat-text);
  line-height: 1;
  letter-spacing: -1px;
}

.donut-core__label {
  font-size: 11px;
  color: var(--wechat-text-secondary);
  margin-top: 3px;
  font-weight: 500;
}

/* Status Cards */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
}

.status-card {
  background: var(--wechat-bg);
  border: 1px solid var(--wechat-border-light);
  border-radius: var(--radius-md);
  padding: 12px 14px;
  transition: transform 200ms ease, box-shadow 200ms ease;
  position: relative;
  overflow: hidden;
}

.status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 3px;
  height: 100%;
  background: var(--status-color);
  border-radius: 0 2px 2px 0;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.status-card__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.status-card__name {
  font-size: 12px;
  color: var(--wechat-text-secondary);
  font-weight: 500;
}

.status-card__count {
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.5px;
}

.status-card__bar-track {
  height: 4px;
  background: var(--wechat-border-light);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
}

.status-card__bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 2px;
}

.status-card__bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-card__pct {
  font-size: 12px;
  font-weight: 700;
  color: var(--wechat-text);
}

.status-card__pct-label {
  font-size: 11px;
  color: var(--wechat-text-placeholder);
}

/* ── Usage Rate Section ── */
.usage-section {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
  align-items: center;
}

@media (max-width: 640px) {
  .usage-section {
    grid-template-columns: 1fr;
  }
}

/* Usage Gauge */
.usage-gauge-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.usage-gauge {
  position: relative;
  width: 120px;
  height: 120px;
}

.gauge-svg {
  width: 100%;
  height: 100%;
}

.gauge-fill {
  animation: gauge-reveal 1.2s cubic-bezier(0.4, 0, 0.2, 1) both;
  transition: stroke-dasharray 1s ease;
}

@keyframes gauge-reveal {
  from {
    stroke-dasharray: 0 314.16;
  }
}

.gauge-label {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.gauge-label__pct {
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -1px;
}

.gauge-label__txt {
  font-size: 11px;
  color: var(--wechat-text-secondary);
  margin-top: 2px;
  font-weight: 500;
}

.usage-summary {
  display: flex;
  align-items: center;
  gap: 0;
  width: 100%;
  background: var(--wechat-bg);
  border: 1px solid var(--wechat-border-light);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.usage-summary__item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 6px;
  gap: 2px;
}

.usage-summary__num {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}

.usage-summary__desc {
  font-size: 10px;
  color: var(--wechat-text-secondary);
  font-weight: 500;
}

.usage-summary__divider {
  width: 1px;
  height: 36px;
  background: var(--wechat-border-light);
  flex-shrink: 0;
}

/* Rate Bars */
.rate-bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.rate-bar-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rate-bar-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rate-bar-item__info {
  display: flex;
  align-items: center;
  gap: 7px;
}

.rate-bar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.rate-bar-item__name {
  font-size: 13px;
  color: var(--wechat-text-secondary);
  font-weight: 500;
}

.rate-bar-item__nums {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.rate-bar-item__count {
  font-size: 15px;
  font-weight: 800;
  line-height: 1;
}

.rate-bar-item__total {
  font-size: 11px;
  color: var(--wechat-text-placeholder);
}

.rate-bar-track {
  height: 8px;
  background: var(--wechat-bg);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--wechat-border-light);
}

.rate-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 2px;
}

.rate-bar-fill--animated {
  background-size: 20px 20px;
  animation: bar-stripes 1s linear infinite;
}

@keyframes bar-stripes {
  from { background-position: 0 0; }
  to { background-position: 20px 0; }
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
/* UNIQUE_BUILD_MARKER_1774576057 */
