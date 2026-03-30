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
        <div class="stat-card" @click="$router.push('/assets')">
          <div class="stat-card__icon stat-card__icon--primary"><el-icon><Box /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalAssets || 0 }}</div>
            <div class="stat-card__label">资产总数</div>
          </div>
          <div class="stat-card__arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card" @click="$router.push('/categories')">
          <div class="stat-card__icon stat-card__icon--info"><el-icon><Grid /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalCategories || 0 }}</div>
            <div class="stat-card__label">资产分类</div>
          </div>
          <div class="stat-card__arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card" @click="$router.push('/departments')">
          <div class="stat-card__icon stat-card__icon--success"><el-icon><OfficeBuilding /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ stats.totalDepartments || 0 }}</div>
            <div class="stat-card__label">部门</div>
          </div>
          <div class="stat-card__arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card">
          <div class="stat-card__icon stat-card__icon--warning"><el-icon><Bottom /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">—</div>
            <div class="stat-card__label">今日入库</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card" @click="showReminderDialog = true">
          <div class="stat-card__icon stat-card__icon--danger"><el-icon><Clock /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ reminderStats.warrantyExpiring7Days || 0 }}</div>
            <div class="stat-card__label">7天内到期</div>
          </div>
          <div class="stat-card__arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <div class="stat-card" @click="showReminderDialog = true">
          <div class="stat-card__icon stat-card__icon--warning2"><el-icon><Warning /></el-icon></div>
          <div class="stat-card__body">
            <div class="stat-card__value">{{ reminderStats.maintenanceDue30Days || 0 }}</div>
            <div class="stat-card__label">30天维保</div>
          </div>
          <div class="stat-card__arrow"><el-icon><ArrowRight /></el-icon></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="12" class="depreciation-row anim-stagger" style="animation-delay: 0.1s">
      <el-col :xs="12" :sm="6">
        <div class="mini-card">
          <div class="mini-card__label">总原值</div>
          <div class="mini-card__value">{{ fmtMoney(depreciationSummary.totalOriginalValue) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="mini-card">
          <div class="mini-card__label">总净值</div>
          <div class="mini-card__value">{{ fmtMoney(depreciationSummary.totalCurrentValue) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="mini-card">
          <div class="mini-card__label">总折旧</div>
          <div class="mini-card__value">{{ fmtMoney(depreciationSummary.totalAccumulatedDepreciation) }}</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="mini-card">
          <div class="mini-card__label">折旧率</div>
          <div class="mini-card__value">{{ depreciationSummary.totalDepreciationRate }}%</div>
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
                <circle cx="110" cy="110" r="82" fill="none" stroke="var(--border)" stroke-width="18" />
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
        
        <div class="panel anim-fade-in-up" style="animation-delay:200ms">
          <div class="panel__header">
            <span class="panel__title">🕐 最近添加的资产</span>
            <el-button size="small" type="primary" plain @click="$router.push('/assets')">全部资产</el-button>
          </div>
          <div class="panel__body" style="padding:0">
            <div v-if="stats.recentAssets?.length" class="recent-table-wrap">
              <el-table :data="stats.recentAssets" class="recent-table">
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
            </div>
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
              <template #image><el-icon :size="44" color="var(--border)"><Document /></el-icon></template>
            </el-empty>
          </div>
        </div>
        <div class="panel anim-fade-in-up" style="animation-delay:170ms">
          <div class="panel__header"><span class="panel__title">⚡ 快捷操作</span></div>
          <div class="panel__body">
            <div class="quick-actions">
              <div class="quick-action" @click="$router.push('/assets/create')">
                <div class="quick-action__icon quick-action__icon--primary"><el-icon><Plus /></el-icon></div>
                <span class="quick-action__label">添加资产</span>
              </div>
              <div class="quick-action" @click="$router.push('/purchases')">
                <div class="quick-action__icon quick-action__icon--warning"><el-icon><ShoppingCart /></el-icon></div>
                <span class="quick-action__label">采购申请</span>
              </div>
              <div class="quick-action" @click="$router.push('/categories')">
                <div class="quick-action__icon quick-action__icon--info"><el-icon><Grid /></el-icon></div>
                <span class="quick-action__label">资产分类</span>
              </div>
              <div class="quick-action" @click="$router.push('/reports/depreciation')">
                <div class="quick-action__icon quick-action__icon--success"><el-icon><TrendCharts /></el-icon></div>
                <span class="quick-action__label">折旧报表</span>
              </div>
              <div class="quick-action" @click="$router.push('/asset-transfers')">
                <div class="quick-action__icon quick-action__icon--purple"><el-icon><RefreshRight /></el-icon></div>
                <span class="quick-action__label">资产转移</span>
              </div>
              <div class="quick-action" @click="$router.push('/settings')">
                <div class="quick-action__icon quick-action__icon--muted"><el-icon><Setting /></el-icon></div>
                <span class="quick-action__label">系统设置</span>
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
import { depreciationApi } from '@/api/depreciation'
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

const depreciationSummary = ref({
  totalOriginalValue: 0,
  totalCurrentValue: 0,
  totalAccumulatedDepreciation: 0,
  totalDepreciationRate: '0.00'
})
const currentTime = ref(dayjs().format('HH:mm'))
const currentDate = computed(() => dayjs().format('YYYY年MM月DD日'))
const currentWeekday = computed(() => ['周日','周一','周二','周三','周四','周五','周六'][dayjs().day()])
const greetingText = computed(() => { const h = dayjs().hour(); if (h<5) return '凌晨好'; if (h<12) return '上午好'; if (h<14) return '中午好'; if (h<18) return '下午好'; return '晚上好' })
let timeTimer: ReturnType<typeof setInterval>
onMounted(() => { timeTimer = setInterval(() => { currentTime.value = dayjs().format('HH:mm') }, 60000) })
onUnmounted(() => { clearInterval(timeTimer) })
const statusColorMap: Record<string, string> = { inUse: 'var(--primary)', idle: '#909399', maintenance: '#FF991A', retired: '#FA5151', scrapped: '#C0C4CC' }
const statusLabelMap: Record<string, string> = { inUse: '使用中', idle: '闲置', maintenance: '维护中', retired: '已退役', scrapped: '已报废' }
const statusOrder = ['inUse','idle','maintenance','retired','scrapped']
function statusLabel(status: string) { return statusLabelMap[status] || status }
function statusTagType(status: string) { const m: Record<string, string> = { inUse:'success', idle:'info', maintenance:'warning', retired:'danger', scrapped:'info' }; return m[status] || 'info' }
function formatDate(date: string | null | undefined) { if (!date) return '—'; return dayjs(date).format('YYYY-MM-DD HH:mm') }
function formatDateShort(date: string | null | undefined) { if (!date) return '—'; return dayjs(date).format('MM/DD HH:mm') }
function fmtMoney(val: number | string) { const n = Number(val) || 0; return '¥' + n.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) }
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

async function fetchDepreciation() {
  try {
    const r = await depreciationApi.list({ page: 1, page_size: 1 })
    if (r.data?.summary) {
      const s = r.data.summary
      depreciationSummary.value = {
        totalOriginalValue: s.totalOriginalValue,
        totalCurrentValue: s.totalCurrentValue,
        totalAccumulatedDepreciation: s.totalAccumulatedDepreciation,
        totalDepreciationRate: Number(s.totalDepreciationRate).toFixed(1)
      }
    }
  } catch (e) { console.error(e) }
}
async function fetchSettings() { try { const r = await settingsApi.get(); if (r.data) { const d = r.data as any; settings.value.systemName = d.systemName || d.siteTitle || 'IT 资产管理系统'; settings.value.logoUrl = d.logoUrl || ''; settings.value.faviconUrl = d.faviconUrl || ''; settings.value.announcement = d.announcement || ''; settings.value.announcement_enabled = d.announcementEnabled ?? false } } catch (e) { console.error(e) } }
onMounted(async () => {
  await Promise.all([
    fetchStats(),
    fetchSettings().catch(() => {}),
    assetStore.fetchOptions().catch(() => {}),
    fetchReminders().catch(() => {}),
    fetchDepreciation().catch(() => {})
  ])
})
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
.announcement-bar { background: linear-gradient(135deg,#3B82F6 0%,#2563EB 100%); color: #fff; overflow: hidden; border-radius: var(--radius-lg); margin-bottom: 14px; box-shadow: 0 4px 16px rgba(59,130,246,0.35); }
.announcement-inner { display: flex; align-items: center; padding: 10px 0; animation: marquee 28s linear infinite; }
.announcement-icon { font-size: 16px; flex-shrink: 0; padding: 0 12px; }
.announcement-text { font-size: 13px; font-weight: 500; white-space: nowrap; }

/* Brand Header */
.brand-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; margin-bottom: 14px; background: var(--card-bg); border-radius: var(--radius-xl); box-shadow: var(--shadow-sm); border: 1px solid var(--border); position: relative; overflow: hidden; }
.brand-header::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg,rgba(26,173,25,0.07) 0%,transparent 60%,rgba(26,173,25,0.03) 100%); pointer-events: none; }
.brand-header__orb { position: absolute; top: -28px; right: 70px; width: 130px; height: 130px; border-radius: 50%; background: radial-gradient(circle,rgba(26,173,25,0.13) 0%,transparent 70%); pointer-events: none; animation: orb-pulse 4s ease-in-out infinite; }
.brand-header__left { display: flex; align-items: center; gap: 14px; position: relative; }
.brand-header__logo img { width: 42px; height: 42px; border-radius: 10px; object-fit: contain; }
.brand-header__icon { font-size: 38px; width: 46px; height: 46px; display: flex; align-items: center; justify-content: center; }
.brand-header__name { font-size: 19px; font-weight: 700; color: var(--text-primary); line-height: 1.3; }
.brand-header__sub { font-size: 13px; color: var(--text-secondary); margin-top: 3px; }
.brand-header__right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; position: relative; }
.brand-header__date { font-size: 12px; color: var(--text-secondary); }
.brand-header__time { font-size: 24px; font-weight: 700; color: var(--primary); font-family: 'SF Mono','Monaco','Inconsolata',monospace; line-height: 1; }

/* Stat Cards */
.stats-grid { margin-bottom: 12px; }

.stat-card { display: flex; align-items: center; gap: 12px; padding: 14px 14px; border-radius: var(--radius-lg); cursor: pointer; margin-bottom: 8px; background: var(--card-bg); border: 1px solid var(--border); box-shadow: var(--shadow-sm); transition: transform 240ms cubic-bezier(0.4,0,0.2,1), box-shadow 240ms cubic-bezier(0.4,0,0.2,1), border-color var(--transition-fast); }
.stat-card:hover { transform: translateY(-3px) scale(1.01); box-shadow: var(--shadow-md); border-color: var(--border-hover); }
.stat-card__icon { width: 42px; height: 42px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.stat-card__icon--primary  { background: var(--primary-bg);  color: var(--primary); }
.stat-card__icon--info     { background: var(--info-bg);     color: var(--info); }
.stat-card__icon--success  { background: var(--success-bg);  color: var(--success); }
.stat-card__icon--warning  { background: var(--warning-bg);   color: var(--warning); }
.stat-card__icon--warning2 { background: var(--warning-bg);   color: var(--warning); }
.stat-card__icon--danger   { background: var(--danger-bg);   color: var(--danger); }
.stat-card__body { flex: 1; min-width: 0; }
.stat-card__value { font-size: 22px; font-weight: 800; color: var(--text-primary); line-height: 1.1; letter-spacing: -0.5px; }
.stat-card__label { font-size: 12px; color: var(--text-secondary); font-weight: 500; margin-top: 2px; }
.stat-card__arrow { color: var(--text-muted); font-size: 16px; flex-shrink: 0; transition: transform var(--transition-fast), color var(--transition-fast); }
.stat-card:hover .stat-card__arrow { transform: translateX(3px); color: var(--primary); }

.depreciation-row { margin-bottom: 14px; }
.mini-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 14px 16px; margin-bottom: 8px; box-shadow: var(--shadow-xs); transition: box-shadow var(--transition-fast), transform var(--transition-fast); }
.mini-card:hover { box-shadow: var(--shadow-sm); transform: translateY(-2px); }
.mini-card__label { font-size: 12px; color: var(--text-secondary); font-weight: 500; margin-bottom: 6px; }
.mini-card__value { font-size: 17px; font-weight: 700; color: var(--text-primary); font-family: var(--font-mono); }



/* Panel */
.panel { background: var(--card-bg); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); border: 1px solid var(--border); overflow: hidden; margin-bottom: 14px; transition: box-shadow 240ms ease; }
.panel:hover { box-shadow: 0 6px 24px rgba(0,0,0,0.1); }
.panel--accent { border-color: rgba(26,173,25,0.2); }
.panel__header { display: flex; align-items: center; gap: 10px; padding: 13px 18px; border-bottom: 1px solid var(--border); }
.panel__title { font-size: 14px; font-weight: 600; color: var(--text-primary); flex: 1; }
.panel__badge { font-size: 12px; color: var(--text-secondary); background: var(--bg-page); padding: 2px 10px; border-radius: 10px; }
.panel__badge--danger { background: #FA5151; color: #fff; padding: 2px 9px; border-radius: 10px; font-weight: 700; }
.panel__badge--accent { background: var(--primary); color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: 600; }
.panel__body { padding: 18px; }

/* Status Ring Layout */
.status-ring-layout { display: grid; grid-template-columns: 200px 1fr; gap: 24px; align-items: center; }
@media (max-width: 640px) { .status-ring-layout { grid-template-columns: 1fr; } }
.ring-chart-wrap { position: relative; width: 180px; height: 180px; justify-self: center; }
.ring-svg { width: 100%; height: 100%; filter: drop-shadow(0 2px 10px rgba(0,0,0,0.08)); }
.ring-seg { transform-origin: center; animation: donut-reveal 0.8s cubic-bezier(0.4,0,0.2,1) both; }
.ring-core { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-core__pct { font-size: 28px; font-weight: 800; color: var(--text-primary); line-height: 1; letter-spacing: -1px; }
.ring-core__sub { font-size: 11px; color: var(--text-secondary); margin-top: 4px; font-weight: 500; }
.ring-legend { display: flex; flex-direction: column; gap: 12px; }
.ring-legend__item { display: flex; flex-direction: column; gap: 5px; }
.ring-legend__top { display: flex; align-items: center; gap: 8px; }
.ring-legend__dot { width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }
.ring-legend__name { font-size: 13px; color: var(--text-secondary); flex: 1; font-weight: 500; }
.ring-legend__count { font-size: 17px; font-weight: 800; line-height: 1; }
.ring-legend__track { height: 5px; background: var(--bg-page); border-radius: 3px; overflow: hidden; border: 1px solid var(--border); }
.ring-legend__fill { height: 100%; border-radius: 3px; transition: width 1s cubic-bezier(0.4,0,0.2,1); min-width: 3px; }

/* Recent Table */
.asset-code { font-family: var(--font-mono); font-size: 12px; color: var(--primary); background: var(--primary-bg); padding: 2px 7px; border-radius: 5px; }
.price-text { font-weight: 600; color: var(--text-primary); }
.date-text { color: var(--text-secondary); font-size: 12px; }
:deep(.el-table) { --el-table-border-color: var(--border); --el-table-header-bg-color: var(--bg-page); }
:deep(.el-table .el-table__row:hover > td) { background: var(--bg-page) !important; }

/* Purchase List */
.purchase-list { display: flex; flex-direction: column; }
.purchase-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 8px; border-bottom: 1px solid var(--border); gap: 10px; transition: background-color var(--transition-fast); }
.purchase-item:hover { background: var(--bg-page); }
.purchase-item__left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.purchase-item__icon { width: 34px; height: 34px; border-radius: 9px; background: var(--warning-bg); display: flex; align-items: center; justify-content: center; color: var(--warning); font-size: 17px; flex-shrink: 0; }
.purchase-item__info { display: flex; flex-direction: column; min-width: 0; }
.purchase-item__title { font-size: 13px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.purchase-item__meta { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.purchase-item__right { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; flex-shrink: 0; }
.purchase-item__date { font-size: 11px; color: var(--text-muted); }
.purchase-footer { padding: 10px 8px 4px; display: flex; justify-content: center; }

/* Quick Actions */
.quick-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.quick-action { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 8px; border-radius: var(--radius-md); cursor: pointer; transition: background-color var(--transition-fast),transform var(--transition-fast),box-shadow var(--transition-fast); background: var(--bg-page); border: 1px solid var(--border); }
.quick-action:hover { background: var(--bg-hover); transform: translateY(-3px); box-shadow: var(--shadow-sm); }
.quick-action__icon { width: 42px; height: 42px; border-radius: 11px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.quick-action__icon--primary  { background: var(--primary-bg);  color: var(--primary); }
.quick-action__icon--warning  { background: var(--warning-bg);   color: var(--warning); }
.quick-action__icon--info     { background: var(--info-bg);     color: var(--info); }
.quick-action__icon--success  { background: var(--success-bg);  color: var(--success); }
.quick-action__icon--purple   { background: rgba(156,106,222,0.12); color: #9C6ADE; }
.quick-action__icon--muted   { background: var(--bg-page);    color: var(--text-muted); }
.quick-action__label { font-size: 12px; font-weight: 500; color: var(--text-secondary); text-align: center; }
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
  .dashboard { padding: 0 8px 20px; }
}

/* Dialog table */
.dialog-table-wrap { overflow-x: auto; }

/* Recent Table */
.recent-table-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.recent-table { min-width: 600px;
  min-width: 600px;
}
</style>

