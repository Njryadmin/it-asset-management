<template>
  <div class="dashboard">
    <div v-if="settings.announcement_enabled && settings.announcement" class="announcement-bar">
      <div class="announcement-inner">
        <span class="announcement-icon">📢</span>
        <span class="announcement-text">{{ settings.announcement }}&nbsp;&nbsp;&nbsp;&nbsp;{{ settings.announcement }}</span>
      </div>
    </div>
    <div class="brand-header anim-fade-in-up">
      <div class="brand-header__left">
        <div v-if="settings.faviconUrl" class="brand-header__logo">
          <img :src="settings.faviconUrl" :alt="settings.systemName" class="brand-header__logo-img" />
        </div>
        <div v-else class="brand-header__icon">💻</div>
        <div class="brand-header__info">
          <div class="brand-header__name">仪表盘</div>
          <div class="brand-header__sub">{{ greetingText }} · {{ currentWeekday }}</div>
        </div>
      </div>
      <div class="brand-header__right">
        <div class="brand-header__date">{{ currentDate }}</div>
        <div class="brand-header__time">{{ currentTime }}</div>
      </div>
      <div class="brand-header__orb"></div>
    </div>
    <el-row :gutter="14" class="stats-grid anim-stagger">
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--green" @click="$router.push('/assets')">
          <div class="stat-card__glow"></div>
          <div class="stat-card__icon"><el-icon><Box /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalAssets || 0 }}</div>
            <div class="stat-card__label">资产总数</div>
          </div>
          <div class="stat-card__trend"><el-icon><TrendCharts /></el-icon></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--blue" @click="$router.push('/categories')">
          <div class="stat-card__glow stat-card__glow--blue"></div>
          <div class="stat-card__icon"><el-icon><Grid /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalCategories || 0 }}</div>
            <div class="stat-card__label">资产分类</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--orange" @click="$router.push('/suppliers')">
          <div class="stat-card__glow stat-card__glow--orange"></div>
          <div class="stat-card__icon"><el-icon><Shop /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalSuppliers || 0 }}</div>
            <div class="stat-card__label">供应商</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--purple" @click="$router.push('/departments')">
          <div class="stat-card__glow stat-card__glow--purple"></div>
          <div class="stat-card__icon"><el-icon><OfficeBuilding /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalDepartments || 0 }}</div>
            <div class="stat-card__label">部门</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--cyan">
          <div class="stat-card__glow stat-card__glow--cyan"></div>
          <div class="stat-card__icon"><el-icon><Bottom /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ todayInCount }}</div>
            <div class="stat-card__label">今日入库</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--red">
          <div class="stat-card__glow stat-card__glow--red"></div>
          <div class="stat-card__icon"><el-icon><Top /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ todayOutCount }}</div>
            <div class="stat-card__label">今日出库</div>
          </div>
        </div>
      </el-col>
      <!-- Warranty Expiring Warning -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--warning" @click="showReminderDialog = true">
          <div class="stat-card__glow stat-card__glow--warning"></div>
          <div class="stat-card__icon"><el-icon><Clock /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ reminderStats.warrantyExpiring7Days || 0 }}</div>
            <div class="stat-card__label">7天内到期</div>
          </div>
        </div>
      </el-col>
      <!-- Maintenance Due Warning -->
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card stat-card--danger" @click="showReminderDialog = true">
          <div class="stat-card__glow stat-card__glow--danger"></div>
          <div class="stat-card__icon"><el-icon><Warning /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ reminderStats.maintenanceDue30Days || 0 }}</div>
            <div class="stat-card__label">30天维保</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Reminder Dialog -->
    <el-dialog v-model="showReminderDialog" title="⚠️ 维保提醒" width="700px">
      <el-tabs>
        <el-tab-pane label="即将到期">
          <el-empty v-if="warrantyExpiring.length === 0" description="暂无即将到期的资产" />
          <el-table v-else :data="warrantyExpiring" stripe size="small">
            <el-table-column prop="name" label="资产名称" min-width="120" />
            <el-table-column prop="assetCode" label="资产编号" width="120" />
            <el-table-column prop="daysRemaining" label="剩余天数" width="80">
              <template #default="{ row }">
                <el-tag :type="row.daysRemaining <= 7 ? 'danger' : 'warning'" size="small">
                  {{ row.daysRemaining }}天
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="warrantyExpireDate" label="到期日期" width="110">
              <template #default="{ row }">
                {{ row.warrantyExpireDate }}
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="维保提醒">
          <el-empty v-if="maintenanceDue.length === 0" description="暂无维保提醒" />
          <el-table v-else :data="maintenanceDue" stripe size="small">
            <el-table-column prop="name" label="资产名称" min-width="120" />
            <el-table-column prop="assetCode" label="资产编号" width="120" />
            <el-table-column prop="maintenanceType" label="维保类型" width="100" />
            <el-table-column prop="daysRemaining" label="剩余天数" width="80">
              <template #default="{ row }">
                <el-tag :type="row.daysRemaining <= 7 ? 'danger' : 'warning'" size="small">
                  {{ row.daysRemaining }}天
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="nextMaintenanceDate" label="维保日期" width="110" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <el-row :gutter="14" class="content-row">
      <el-col :xs="24" :md="14">
        <div class="panel anim-fade-in-up" style="animation-delay:80ms">
          <div class="panel__header">
            <span class="panel__title">📊 资产状态分布</span>
            <span class="panel__badge">共 {{ stats.totalAssets || 0 }} 项</span>
          </div>
          <div class="panel__body status-ring-layout">
            <div class="ring-chart-wrap">
              <svg viewBox="0 0 220 220" class="ring-svg">
                <circle cx="110" cy="110" r="82" fill="none" stroke="var(--wechat-border-light)" stroke-width="18" />
                <circle v-for="(seg, i) in donutSegments" :key="seg.key" cx="110" cy="110" r="82" fill="none"
                  :stroke="seg.color" stroke-width="18" :stroke-dasharray="seg.dashArray" :stroke-dashoffset="seg.dashOffset"
                  stroke-linecap="butt" class="ring-seg" :style="{ animationDelay: i * 100 + 'ms' }" />
              </svg>
              <div class="ring-core">
                <span class="ring-core__pct">{{ overallUsagePct }}%</span>
                <span class="ring-core__sub">使用率</span>
              </div>
            </div>
            <div class="ring-legend">
              <div v-for="item in statusCardItems" :key="item.key" class="ring-legend__item">
                <div class="ring-legend__top">
                  <span class="ring-legend__dot" :style="{ background: item.color }"></span>
                  <span class="ring-legend__name">{{ item.label }}</span>
                  <span class="ring-legend__count" :style="{ color: item.color }">{{ item.count }}</span>
                </div>
                <div class="ring-legend__track">
                  <div class="ring-legend__fill" :style="{ width: item.pct + '%', background: item.color }"></div>
                </div>
              </div>
              <el-empty v-if="!hasStatusData" description="暂无数据" :image-size="50" />
            </div>
          </div>
        </div>
        <div class="panel anim-fade-in-up" style="animation-delay:140ms">
          <div class="panel__header">
            <span class="panel__title">📈 资产使用率</span>
            <span class="panel__badge panel__badge--accent">整体 {{ overallUsagePct }}%</span>
          </div>
          <div class="panel__body usage-layout">
            <div class="arc-wrap">
              <svg viewBox="0 0 200 120" class="arc-svg">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="var(--wechat-border-light)" stroke-width="16" stroke-linecap="round" />
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" :stroke="usageGaugeColor" stroke-width="16" stroke-linecap="round"
                  :stroke-dasharray="arcDashArray" stroke-dashoffset="0" class="arc-fill" />
              </svg>
              <div class="arc-center">
                <span class="arc-center__pct" :style="{ color: usageGaugeColor }">{{ overallUsagePct }}%</span>
                <span class="arc-center__label">使用率</span>
              </div>
              <div class="arc-ticks">
                <span class="arc-tick arc-tick--0">0%</span>
                <span class="arc-tick arc-tick--50">50%</span>
                <span class="arc-tick arc-tick--100">100%</span>
              </div>
            </div>
            <div class="usage-pills">
              <div class="usage-pill usage-pill--green">
                <span class="usage-pill__dot"></span>
                <span class="usage-pill__label">在用</span>
                <span class="usage-pill__count">{{ stats.assetsByStatus?.inUse || 0 }}</span>
              </div>
              <div class="usage-pill usage-pill--gray">
                <span class="usage-pill__dot"></span>
                <span class="usage-pill__label">闲置</span>
                <span class="usage-pill__count">{{ stats.assetsByStatus?.idle || 0 }}</span>
              </div>
              <div class="usage-pill usage-pill--orange">
                <span class="usage-pill__dot"></span>
                <span class="usage-pill__label">维护</span>
                <span class="usage-pill__count">{{ stats.assetsByStatus?.maintenance || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="panel anim-fade-in-up" style="animation-delay:200ms">
          <div class="panel__header">
            <span class="panel__title">🕐 最近添加的资产</span>
            <el-button size="small" type="primary" plain @click="$router.push('/assets')">全部资产</el-button>
          </div>
          <div class="panel__body" style="padding:0">
            <el-table v-if="stats.recentAssets?.length" :data="stats.recentAssets" style="width:100%" class="recent-table">
              <el-table-column prop="name" label="资产名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="assetCode" label="编号" width="130">
                <template #default="{ row }"><span class="asset-code">{{ row.assetCode || '—' }}</span></template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="95">
                <template #default="{ row }">
                  <el-tag size="small" :type="statusTagType(row.status)" effect="light" round>{{ statusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="purchasePrice" label="价格" width="110">
                <template #default="{ row }"><span class="price-text">{{ row.purchasePrice ? '¥' + Number(row.purchasePrice).toLocaleString() : '—' }}</span></template>
              </el-table-column>
              <el-table-column prop="createdAt" label="添加时间" width="155">
                <template #default="{ row }"><span class="date-text">{{ formatDate(row.createdAt) }}</span></template>
              </el-table-column>
              <el-table-column label="操作" width="90" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="$router.push('/assets/' + row.id + '/edit')">详情</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-else description="暂无资产记录" :image-size="60">
              <el-button type="primary" @click="$router.push('/assets/create')">立即添加</el-button>
            </el-empty>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="10">
        <div class="panel panel--accent anim-fade-in-up" style="animation-delay:110ms">
          <div class="panel__header">
            <span class="panel__title">⏳ 待审批采购</span>
            <span v-if="stats.pendingPurchaseRequests?.length" class="panel__badge panel__badge--danger">{{ stats.pendingPurchaseRequests.length }}</span>
          </div>
          <div class="panel__body">
            <div v-if="stats.pendingPurchaseRequests?.length" class="purchase-list">
              <div v-for="req in stats.pendingPurchaseRequests.slice(0, 8)" :key="req.id" class="purchase-item">
                <div class="purchase-item__left">
                  <div class="purchase-item__icon"><el-icon><Document /></el-icon></div>
                  <div class="purchase-item__info">
                    <span class="purchase-item__title">{{ req.title }}</span>
                    <span class="purchase-item__meta">数量 × {{ req.quantity }}<span v-if="req.estimatedPrice"> · ¥{{ req.estimatedPrice.toLocaleString() }}</span></span>
                  </div>
                </div>
                <div class="purchase-item__right">
                  <el-tag size="small" type="warning" effect="light" round>待审批</el-tag>
                  <span class="purchase-item__date">{{ formatDateShort(req.createdAt) }}</span>
                </div>
              </div>
              <div class="purchase-footer">
                <el-button size="small" type="primary" plain @click="$router.push('/purchases')">查看全部</el-button>
              </div>
            </div>
            <el-empty v-else description="暂无待审批申请" :image-size="50">
              <template #image><el-icon :size="44" color="var(--wechat-border-light)"><Document /></el-icon></template>
            </el-empty>
          </div>
        </div>
        <div class="panel anim-fade-in-up" style="animation-delay:170ms">
          <div class="panel__header"><span class="panel__title">⚡ 快捷操作</span></div>
          <div class="panel__body">
            <div class="quick-actions">
              <div class="quick-action" @click="$router.push('/assets/create')">
                <div class="quick-action__icon quick-action__icon--green"><el-icon><Plus /></el-icon></div>
                <span class="quick-action__label">添加资产</span>
              </div>
              <div class="quick-action" @click="$router.push('/purchases')">
                <div class="quick-action__icon quick-action__icon--orange"><el-icon><ShoppingCart /></el-icon></div>
                <span class="quick-action__label">采购申请</span>
              </div>
              <div class="quick-action" @click="$router.push('/categories')">
                <div class="quick-action__icon quick-action__icon--blue"><el-icon><Grid /></el-icon></div>
                <span class="quick-action__label">资产分类</span>
              </div>
              <div class="quick-action" @click="$router.push('/suppliers')">
                <div class="quick-action__icon quick-action__icon--purple"><el-icon><Shop /></el-icon></div>
                <span class="quick-action__label">供应商</span>
              </div>
            </div>
          </div>
        </div>
        <div class="panel anim-fade-in-up" style="animation-delay:230ms">
          <div class="panel__header"><span class="panel__title">🖥️ 系统概览</span></div>
          <div class="panel__body">
            <div class="summary-list">
              <div class="summary-item" @click="$router.push('/assets')">
                <span class="summary-item__icon">📦</span><span class="summary-item__label">资产总数</span>
                <span class="summary-item__value summary-item__value--primary">{{ stats.totalAssets || 0 }}</span>
              </div>
              <div class="summary-item" @click="$router.push('/categories')">
                <span class="summary-item__icon">🏷️</span><span class="summary-item__label">分类数</span>
                <span class="summary-item__value">{{ stats.totalCategories || 0 }}</span>
              </div>
              <div class="summary-item" @click="$router.push('/suppliers')">
                <span class="summary-item__icon">🏪</span><span class="summary-item__label">供应商</span>
                <span class="summary-item__value">{{ stats.totalSuppliers || 0 }}</span>
              </div>
              <div class="summary-item" @click="$router.push('/departments')">
                <span class="summary-item__icon">🏢</span><span class="summary-item__label">部门</span>
                <span class="summary-item__value">{{ stats.totalDepartments || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-item__icon">👤</span><span class="summary-item__label">用户</span>
                <span class="summary-item__value">{{ stats.totalUsers || 0 }}</span>
              </div>
              <div class="summary-item" @click="$router.push('/purchases')">
                <span class="summary-item__icon">📋</span><span class="summary-item__label">采购申请</span>
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
import { remindersApi } from '@/api/reminders'
import type { DashboardStats } from '@/types'
import { useAssetStore } from '@/stores/assets'
import dayjs from 'dayjs'

const assetStore = useAssetStore()
const settings = ref({ systemName: 'IT 资产管理系统', logoUrl: '', faviconUrl: '', announcement: '', announcement_enabled: false })
const stats = ref<DashboardStats & { todayIn?: number; todayOut?: number }>({
  totalAssets: 0, totalCategories: 0, totalSuppliers: 0, totalDepartments: 0,
  totalUsers: 0, totalPurchaseRequests: 0, assetsByStatus: {}, assetsByCategory: {},
  recentAssets: [], pendingPurchaseRequests: [],
})
const reminderStats = ref({ warrantyExpiring7Days: 0, warrantyExpiring30Days: 0, maintenanceDue30Days: 0 })
const warrantyExpiring = ref<any[]>([])
const maintenanceDue = ref<any[]>([])
const showReminderDialog = ref(false)
const currentTime = ref(dayjs().format('HH:mm'))
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))
const currentWeekday = computed(() => ['周日','周一','周二','周三','周四','周五','周六'][dayjs().day()])
const greetingText = computed(() => { const h = dayjs().hour(); if (h<5) return '凌晨好'; if (h<12) return '上午好'; if (h<14) return '中午好'; if (h<18) return '下午好'; return '晚上好' })
let timeTimer: ReturnType<typeof setInterval>
onMounted(() => { timeTimer = setInterval(() => { currentTime.value = dayjs().format('HH:mm') }, 60000) })
onUnmounted(() => { clearInterval(timeTimer) })
const todayInCount = computed(() => {
  const s = stats.value as any
  if (s.todayIn !== undefined) return s.todayIn
  const today = dayjs().format('YYYY-MM-DD')
  return (stats.value.recentAssets || []).filter((a: any) => a.purchaseDate === today || (a.createdAt && dayjs(a.createdAt).format('YYYY-MM-DD') === today)).length
})
const todayOutCount = computed(() => { const s = stats.value as any; if (s.todayOut !== undefined) return s.todayOut; return 0 })
const statusColorMap: Record<string, string> = { inUse: 'var(--wechat-primary)', idle: '#909399', maintenance: '#FF991A', retired: '#FA5151', scrapped: '#C0C4CC' }
const statusLabelMap: Record<string, string> = { inUse: '使用中', idle: '闲置', maintenance: '维护中', retired: '已退役', scrapped: '已报废' }
const statusOrder = ['inUse','idle','maintenance','retired','scrapped']
function statusLabel(status: string) { return statusLabelMap[status] || status }
function statusTagType(status: string) { const m: Record<string, string> = { inUse:'success', idle:'info', maintenance:'warning', retired:'danger', scrapped:'info' }; return m[status] || 'info' }
function formatDate(date: string | null | undefined) { if (!date) return '—'; return dayjs(date).format('YYYY-MM-DD HH:mm') }
function formatDateShort(date: string | null | undefined) { if (!date) return '—'; return dayjs(date).format('MM/DD HH:mm') }
const hasStatusData = computed(() => Object.values(stats.value.assetsByStatus || {}).some((v: any) => v > 0))
const CIRCUMFERENCE = 2 * Math.PI * 82
interface DonutSeg { key: string; color: string; dashArray: string; dashOffset: string }
const donutSegments = computed<DonutSeg[]>(() => {
  const total = stats.value.totalAssets || 0
  if (!total) return []
  const segments: DonutSeg[] = []; let accumulated = 0
  for (const key of statusOrder) {
    const count = (stats.value.assetsByStatus as any)?.[key] || 0
    if (!count) continue
    const pct = count / total; const arcLen = pct * CIRCUMFERENCE; const gapLen = CIRCUMFERENCE - arcLen
    segments.push({ key, color: statusColorMap[key] || '#909399', dashArray: `${arcLen.toFixed(2)} ${gapLen.toFixed(2)}`, dashOffset: (-accumulated * CIRCUMFERENCE).toFixed(2) })
    accumulated += pct
  }
  return segments
})
interface StatusCardItem { key: string; label: string; color: string; count: number; pct: number }
const statusCardItems = computed<StatusCardItem[]>(() => {
  const total = stats.value.totalAssets || 0
  return statusOrder.map(key => { const count = (stats.value.assetsByStatus as any)?.[key] || 0; return { key, label: statusLabelMap[key] || key, color: statusColorMap[key] || '#909399', count, pct: total ? Math.round((count / total) * 100) : 0 } })
})
const overallUsagePct = computed(() => { const total = stats.value.totalAssets || 0; if (!total) return 0; return Math.round(((stats.value.assetsByStatus as any)?.inUse || 0) / total * 100) })
const usageGaugeColor = computed(() => { const p = overallUsagePct.value; if (p >= 70) return 'var(--wechat-primary)'; if (p >= 40) return '#FF991A'; return '#909399' })
const ARC_LENGTH = Math.PI * 80
const arcDashArray = computed(() => { const pct = Math.min(overallUsagePct.value, 100) / 100; return `${(pct * ARC_LENGTH).toFixed(2)} ${ARC_LENGTH.toFixed(2)}` })
async function fetchStats() { try { const r = await dashboardApi.getStats(); stats.value = r.data } catch (e) { console.error(e) } }
async function fetchReminders() {
  try {
    const [summary, warranty, maintenance] = await Promise.all([
      remindersApi.getSummary(),
      remindersApi.getWarrantyExpiring(30),
      remindersApi.getMaintenanceDue(30)
    ])
    reminderStats.value = summary.data
    warrantyExpiring.value = warranty.data.items
    maintenanceDue.value = maintenance.data.items
  } catch (e) { console.error(e) }
}
async function fetchSettings() { try { const r = await settingsApi.get(); if (r.data) { const d = r.data as any; settings.value.systemName = d.systemName || d.siteTitle || 'IT 资产管理系统'; settings.value.logoUrl = d.logoUrl || ''; settings.value.faviconUrl = d.faviconUrl || ''; settings.value.announcement = d.announcement || ''; settings.value.announcement_enabled = d.announcementEnabled ?? false } } catch (e) { console.error(e) } }
onMounted(async () => { await Promise.all([fetchStats(), fetchSettings().catch(() => {}), assetStore.fetchOptions().catch(() => {}), fetchReminders()]) })
</script>


<style scoped>
@keyframes fade-in-up { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
@keyframes donut-reveal { from { opacity: 0.3; } to { opacity: 1; } }
@keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
@keyframes orb-pulse { 0%,100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.08); } }
@keyframes arc-reveal { from { stroke-dasharray: 0 251.33; } to { } }

.anim-fade-in-up { animation: fade-in-up 0.45s cubic-bezier(0.4,0,0.2,1) both; }
.anim-stagger    { animation: fade-in-up 0.45s cubic-bezier(0.4,0,0.2,1) 0.06s both; }

.dashboard { max-width: 1400px; margin: 0 auto; padding: 0 4px 28px; }

/* Announcement */
.announcement-bar { background: linear-gradient(135deg,#ff9500 0%,#ff6b00 100%); color: #fff; overflow: hidden; border-radius: var(--radius-lg); margin-bottom: 14px; box-shadow: 0 4px 16px rgba(255,149,0,0.35); }
.announcement-inner { display: flex; align-items: center; padding: 10px 0; animation: marquee 28s linear infinite; }
.announcement-icon { font-size: 16px; flex-shrink: 0; padding: 0 12px; }
.announcement-text { font-size: 13px; font-weight: 500; white-space: nowrap; }

/* Brand Header */
.brand-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; margin-bottom: 14px; background: var(--wechat-card); border-radius: var(--radius-xl); box-shadow: var(--wechat-shadow-card); border: 1px solid var(--wechat-border-light); position: relative; overflow: hidden; }
.brand-header::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg,rgba(26,173,25,0.07) 0%,transparent 60%,rgba(26,173,25,0.03) 100%); pointer-events: none; }
.brand-header__orb { position: absolute; top: -28px; right: 70px; width: 130px; height: 130px; border-radius: 50%; background: radial-gradient(circle,rgba(26,173,25,0.13) 0%,transparent 70%); pointer-events: none; animation: orb-pulse 4s ease-in-out infinite; }
.brand-header__left { display: flex; align-items: center; gap: 14px; position: relative; }
.brand-header__logo img { width: 42px; height: 42px; border-radius: 10px; object-fit: contain; }
.brand-header__icon { font-size: 38px; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; }
.brand-header__name { font-size: 19px; font-weight: 700; color: var(--wechat-text); line-height: 1.3; }
.brand-header__sub { font-size: 13px; color: var(--wechat-text-secondary); margin-top: 3px; }
.brand-header__right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; position: relative; }
.brand-header__date { font-size: 12px; color: var(--wechat-text-secondary); }
.brand-header__time { font-size: 24px; font-weight: 700; color: var(--wechat-primary); font-family: 'SF Mono','Monaco','Inconsolata',monospace; line-height: 1; }

/* Stat Cards */
.stats-grid { margin-bottom: 14px; }
.stat-card { display: flex; align-items: center; gap: 10px; padding: 14px 12px; border-radius: var(--radius-lg); cursor: pointer; margin-bottom: 8px; transition: transform 240ms cubic-bezier(0.4,0,0.2,1),box-shadow 240ms cubic-bezier(0.4,0,0.2,1); position: relative; overflow: hidden; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
.stat-card:hover { transform: translateY(-4px) scale(1.02); }
.stat-card__glow { position: absolute; bottom: -18px; right: -8px; width: 80px; height: 80px; border-radius: 50%; background: radial-gradient(circle,rgba(255,255,255,0.22) 0%,transparent 70%); pointer-events: none; }
.stat-card__glow--blue   { background: radial-gradient(circle,rgba(64,158,255,0.28) 0%,transparent 70%); }
.stat-card__glow--orange { background: radial-gradient(circle,rgba(255,153,26,0.28) 0%,transparent 70%); }
.stat-card__glow--purple { background: radial-gradient(circle,rgba(156,106,222,0.28) 0%,transparent 70%); }
.stat-card__glow--cyan   { background: radial-gradient(circle,rgba(0,188,212,0.28) 0%,transparent 70%); }
.stat-card__glow--red    { background: radial-gradient(circle,rgba(250,81,81,0.28) 0%,transparent 70%); }
.stat-card__glow--warning { background: radial-gradient(circle,rgba(255,176,32,0.28) 0%,transparent 70%); }
.stat-card__glow--danger  { background: radial-gradient(circle,rgba(255,80,80,0.28) 0%,transparent 70%); }
.stat-card--green  { background: linear-gradient(145deg,#1ead1e 0%,#148a14 100%); box-shadow: 0 6px 22px rgba(26,173,25,0.38),0 2px 8px rgba(26,173,25,0.18); }
.stat-card--green:hover { box-shadow: 0 10px 32px rgba(26,173,25,0.48),0 4px 12px rgba(26,173,25,0.22); }
.stat-card--blue   { background: linear-gradient(145deg,#4fa3ff 0%,#337ecc 100%); box-shadow: 0 6px 22px rgba(64,158,255,0.32),0 2px 8px rgba(64,158,255,0.15); }
.stat-card--orange { background: linear-gradient(145deg,#ffa333 0%,#e68a00 100%); box-shadow: 0 6px 22px rgba(255,153,26,0.32),0 2px 8px rgba(255,153,26,0.15); }
.stat-card--purple { background: linear-gradient(145deg,#a676de 0%,#7b52b5 100%); box-shadow: 0 6px 22px rgba(156,106,222,0.32),0 2px 8px rgba(156,106,222,0.15); }
.stat-card--cyan   { background: linear-gradient(145deg,#00c8d4 0%,#0097a7 100%); box-shadow: 0 6px 22px rgba(0,188,212,0.32),0 2px 8px rgba(0,188,212,0.15); }
.stat-card--red    { background: linear-gradient(145deg,#fa6161 0%,#d94444 100%); box-shadow: 0 6px 22px rgba(250,81,81,0.32),0 2px 8px rgba(250,81,81,0.15); }
.stat-card--warning { background: linear-gradient(145deg,#ffb020 0%,#e69500 100%); box-shadow: 0 6px 22px rgba(255,176,32,0.32),0 2px 8px rgba(255,176,32,0.15); cursor: pointer; }
.stat-card--warning:hover { box-shadow: 0 10px 32px rgba(255,176,32,0.45),0 4px 12px rgba(255,176,32,0.2); }
.stat-card--danger  { background: linear-gradient(145deg,#ff6b6b 0%,#c0392b 100%); box-shadow: 0 6px 22px rgba(255,80,80,0.38),0 2px 8px rgba(255,80,80,0.18); cursor: pointer; }
.stat-card--danger:hover { box-shadow: 0 10px 32px rgba(255,80,80,0.5),0 4px 12px rgba(255,80,80,0.25); }
.stat-card__icon { width: 38px; height: 38px; border-radius: 10px; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 19px; flex-shrink: 0; color: #fff; }
.stat-card__body { flex: 1; min-width: 0; }
.stat-card__value { font-size: 21px; font-weight: 800; color: #fff; line-height: 1.1; letter-spacing: -0.5px; }
.stat-card__label { font-size: 12px; color: rgba(255,255,255,0.85); font-weight: 500; margin-top: 2px; }
.stat-card__trend { width: 28px; height: 28px; border-radius: 8px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.9); font-size: 14px; flex-shrink: 0; }

/* Panel */
.panel { background: var(--wechat-card); border-radius: var(--radius-lg); box-shadow: var(--wechat-shadow-card); border: 1px solid var(--wechat-border-light); overflow: hidden; margin-bottom: 14px; transition: box-shadow 240ms ease; }
.panel:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
.panel--accent { border-color: rgba(26,173,25,0.2); }
.panel__header { display: flex; align-items: center; gap: 10px; padding: 13px 18px; border-bottom: 1px solid var(--wechat-border-light); }
.panel__title { font-size: 14px; font-weight: 600; color: var(--wechat-text); flex: 1; }
.panel__badge { font-size: 12px; color: var(--wechat-text-secondary); background: var(--wechat-bg); padding: 2px 10px; border-radius: 10px; }
.panel__badge--danger { background: #FA5151; color: #fff; padding: 2px 9px; border-radius: 10px; font-weight: 700; }
.panel__badge--accent { background: var(--wechat-primary); color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: 600; }
.panel__body { padding: 18px; }

/* Status Ring Layout */
.status-ring-layout { display: grid; grid-template-columns: 200px 1fr; gap: 24px; align-items: center; }
@media (max-width: 640px) { .status-ring-layout { grid-template-columns: 1fr; } }
.ring-chart-wrap { position: relative; width: 180px; height: 180px; justify-self: center; }
.ring-svg { width: 100%; height: 100%; filter: drop-shadow(0 2px 10px rgba(0,0,0,0.08)); }
.ring-seg { transform-origin: center; animation: donut-reveal 0.8s cubic-bezier(0.4,0,0.2,1) both; }
.ring-core { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-core__pct { font-size: 28px; font-weight: 800; color: var(--wechat-text); line-height: 1; letter-spacing: -1px; }
.ring-core__sub { font-size: 11px; color: var(--wechat-text-secondary); margin-top: 4px; font-weight: 500; }
.ring-legend { display: flex; flex-direction: column; gap: 12px; }
.ring-legend__item { display: flex; flex-direction: column; gap: 5px; }
.ring-legend__top { display: flex; align-items: center; gap: 8px; }
.ring-legend__dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.ring-legend__name { font-size: 13px; color: var(--wechat-text-secondary); flex: 1; font-weight: 500; }
.ring-legend__count { font-size: 17px; font-weight: 800; line-height: 1; }
.ring-legend__track { height: 5px; background: var(--wechat-bg); border-radius: 3px; overflow: hidden; border: 1px solid var(--wechat-border-light); }
.ring-legend__fill { height: 100%; border-radius: 3px; transition: width 1s cubic-bezier(0.4,0,0.2,1); min-width: 3px; }

/* Usage Layout */
.usage-layout { display: flex; align-items: center; gap: 28px; }
@media (max-width: 640px) { .usage-layout { flex-direction: column; align-items: flex-start; } }
.arc-wrap { position: relative; width: 200px; height: 130px; flex-shrink: 0; }
.arc-svg { width: 100%; height: 100%; overflow: visible; }
.arc-fill { animation: arc-reveal 1.2s cubic-bezier(0.4,0,0.2,1) both; transition: stroke-dasharray 0.8s ease; }
.arc-center { position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; }
.arc-center__pct { font-size: 24px; font-weight: 800; line-height: 1; letter-spacing: -1px; }
.arc-center__label { font-size: 11px; color: var(--wechat-text-secondary); margin-top: 3px; font-weight: 500; }
.arc-ticks { position: absolute; bottom: -4px; left: 0; right: 0; display: flex; justify-content: space-between; }
.arc-tick { font-size: 10px; color: var(--wechat-text-placeholder); }
.usage-pills { display: flex; flex-direction: column; gap: 10px; flex: 1; }
.usage-pill { display: flex; align-items: center; gap: 10px; padding: 10px 14px; background: var(--wechat-bg); border: 1px solid var(--wechat-border-light); border-radius: var(--radius-md); transition: transform 200ms ease,box-shadow 200ms ease; }
.usage-pill:hover { transform: translateX(6px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.usage-pill__dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.usage-pill--green  .usage-pill__dot { background: var(--wechat-primary); }
.usage-pill--gray   .usage-pill__dot { background: #909399; }
.usage-pill--orange .usage-pill__dot { background: #FF991A; }
.usage-pill__label { font-size: 13px; color: var(--wechat-text-secondary); flex: 1; font-weight: 500; }
.usage-pill__count { font-size: 18px; font-weight: 800; color: var(--wechat-text); }

/* Recent Table */
.asset-code { font-family: 'SF Mono','Consolas',monospace; font-size: 12px; color: var(--wechat-primary); background: var(--wechat-primary-bg); padding: 2px 7px; border-radius: 5px; }
.price-text { font-weight: 600; color: var(--wechat-text); }
.date-text { color: var(--wechat-text-secondary); font-size: 12px; }
:deep(.el-table) { --el-table-border-color: var(--wechat-border-light); --el-table-header-bg-color: var(--wechat-bg); }
:deep(.el-table .el-table__row:hover > td) { background: var(--wechat-bg) !important; }

/* Purchase List */
.purchase-list { display: flex; flex-direction: column; }
.purchase-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 8px; border-bottom: 1px solid var(--wechat-border-light); gap: 10px; transition: background-color var(--transition-fast); }
.purchase-item:hover { background: var(--wechat-bg); }
.purchase-item__left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.purchase-item__icon { width: 34px; height: 34px; border-radius: 9px; background: rgba(255,153,26,0.12); display: flex; align-items: center; justify-content: center; color: #FF991A; font-size: 17px; flex-shrink: 0; }
.purchase-item__info { display: flex; flex-direction: column; min-width: 0; }
.purchase-item__title { font-size: 13px; font-weight: 600; color: var(--wechat-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.purchase-item__meta { font-size: 12px; color: var(--wechat-text-secondary); margin-top: 2px; }
.purchase-item__right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex-shrink: 0; }
.purchase-item__date { font-size: 11px; color: var(--wechat-text-placeholder); }
.purchase-footer { padding: 10px 8px 4px; display: flex; justify-content: center; }

/* Quick Actions */
.quick-actions { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.quick-action { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 8px; border-radius: var(--radius-md); cursor: pointer; transition: background-color var(--transition-fast),transform var(--transition-fast),box-shadow var(--transition-fast); background: var(--wechat-bg); border: 1px solid var(--wechat-border-light); }
.quick-action:hover { background: var(--wechat-border-light); transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
.quick-action__icon { width: 42px; height: 42px; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.quick-action__icon--green  { background: rgba(26,173,25,0.12);  color: var(--wechat-primary); }
.quick-action__icon--orange { background: rgba(255,153,26,0.12);  color: #FF991A; }
.quick-action__icon--blue   { background: rgba(64,158,255,0.12);  color: #409EFF; }
.quick-action__icon--purple { background: rgba(156,106,222,0.12); color: #9C6ADE; }
.quick-action__label { font-size: 12px; font-weight: 500; color: var(--wechat-text-secondary); text-align: center; }

/* Summary List */
.summary-list { display: flex; flex-direction: column; }
.summary-item { display: flex; align-items: center; gap: 10px; padding: 9px 6px; border-bottom: 1px solid var(--wechat-border-light); transition: background-color var(--transition-fast),transform var(--transition-fast); cursor: pointer; border-radius: var(--radius-sm); }
.summary-item:last-child { border-bottom: none; }
.summary-item:hover { background: var(--wechat-bg); transform: translateX(4px); }
.summary-item__icon { font-size: 16px; width: 26px; text-align: center; flex-shrink: 0; }
.summary-item__label { flex: 1; font-size: 13px; color: var(--wechat-text-secondary); }
.summary-item__value { font-size: 15px; font-weight: 700; color: var(--wechat-text); }
.summary-item__value--primary { color: var(--wechat-primary); }

/* Responsive */
@media (max-width: 768px) {
  .brand-header { padding: 14px 16px; }
  .brand-header__right { align-items: flex-end; }
  .brand-header__time { font-size: 18px; }
  .brand-header__date { font-size: 11px; }
  .brand-header__name { font-size: 16px; }
  .brand-header__sub  { font-size: 11px; }
  .brand-header__orb  { width: 90px; height: 90px; top: -20px; right: 40px; }
  .quick-actions { grid-template-columns: repeat(2, 1fr); }
  .stat-card { margin-bottom: 6px; }
  .panel { margin-bottom: 12px; }
}
@media (max-width: 600px) {
  .stats-grid.el-row { display: flex !important; flex-wrap: wrap !important; gap: 10px !important; margin: 0 !important; }
  .stats-grid .el-col { display: block !important; width: calc(50% - 5px) !important; max-width: calc(50% - 5px) !important; padding: 0 !important; margin: 0 !important; }
  .stat-card { width: 100% !important; display: flex !important; flex-direction: row !important; align-items: center !important; padding: 14px 12px !important; min-height: 88px; margin: 0 !important; }
  .stat-card__body { flex: 1 !important; min-width: 0 !important; }
  .stat-card__value { font-size: 22px !important; }
  .stat-card__label { font-size: 11px !important; }
  .stat-card__icon  { width: 38px !important; height: 38px !important; font-size: 17px !important; margin-right: 8px !important; flex-shrink: 0 !important; }
  .announcement-bar { margin-bottom: 10px; }
  .announcement-text { font-size: 13px !important; }
  .panel { margin-bottom: 12px; }
  .panel__body { padding: 14px !important; }
  .quick-actions { grid-template-columns: repeat(2, 1fr) !important; gap: 8px !important; }
  .quick-action { padding: 12px 6px !important; }
}
@media (max-width: 480px) {
  .stat-card { min-height: 80px; }
  .stat-card__value { font-size: 20px !important; }
}
</style>

