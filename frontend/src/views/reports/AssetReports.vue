<template>
  <div class="reports-page page-container">
    <!-- Summary Cards -->
    <div class="summary-cards anim-fade-in-up">
      <el-card class="summary-card" shadow="hover">
        <div class="summary-card__icon summary-card__icon--primary">
          <el-icon><Box /></el-icon>
        </div>
        <div class="summary-card__content">
          <div class="summary-card__value">{{ summary.total }}</div>
          <div class="summary-card__label">总资产数</div>
        </div>
      </el-card>
      <el-card class="summary-card" shadow="hover">
        <div class="summary-card__icon summary-card__icon--success">
          <el-icon><Plus /></el-icon>
        </div>
        <div class="summary-card__content">
          <div class="summary-card__value">{{ addedThisMonth }}</div>
          <div class="summary-card__label">本月新增</div>
        </div>
      </el-card>
      <el-card class="summary-card" shadow="hover">
        <div class="summary-card__icon summary-card__icon--danger">
          <el-icon><Delete /></el-icon>
        </div>
        <div class="summary-card__content">
          <div class="summary-card__value">{{ scrappedThisMonth }}</div>
          <div class="summary-card__label">本月报废</div>
        </div>
      </el-card>
      <el-card class="summary-card" shadow="hover">
        <div class="summary-card__icon summary-card__icon--info">
          <el-icon><Check /></el-icon>
        </div>
        <div class="summary-card__content">
          <div class="summary-card__value">{{ inUse }}</div>
          <div class="summary-card__label">在用资产</div>
        </div>
      </el-card>
    </div>

    <!-- Filter Bar -->
    <el-card class="filter-card">
      <div class="filter-bar">
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
        <el-select v-model="filterParams.department_id" placeholder="选择部门" clearable style="width: 160px" @change="fetchDistribution">
          <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
        </el-select>
        <el-select v-model="filterParams.category_id" placeholder="选择分类" clearable style="width: 160px" @change="fetchDistribution">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="fetchAll">刷新</el-button>
        <el-button @click="exportCsv">
          <el-icon><Download /></el-icon>
          导出 CSV
        </el-button>
      </div>
    </el-card>

    <!-- Tab Navigation -->
    <el-card class="tab-card">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="分类分布" name="category" />
        <el-tab-pane label="状态分布" name="status" />
        <el-tab-pane label="部门分布" name="department" />
        <el-tab-pane label="重要度分布" name="importance" />
        <el-tab-pane label="资产趋势" name="trend" />
      </el-tabs>
    </el-card>

    <!-- Charts Grid -->
    <div class="charts-grid anim-fade-in-up">
      <!-- Category Tab -->
      <template v-if="activeTab === 'category'">
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">资产分类分布</span>
              <el-select v-model="categoryChartType" size="small" style="width: 120px">
                <el-option label="饼图" value="pie" />
                <el-option label="柱状图" value="bar" />
              </el-select>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container" v-loading="chartsLoading" />
        </el-card>
        <el-card class="chart-card chart-card--wide" v-if="distribution.byCategory.length === 0 && !chartsLoading">
          <el-empty description="暂无分类数据">
            <template #image>
              <div style="font-size: 48px; text-align: center;">📭</div>
            </template>
          </el-empty>
        </el-card>
      </template>

      <!-- Status Tab -->
      <template v-if="activeTab === 'status'">
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">资产状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container" v-loading="chartsLoading" />
        </el-card>
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <span class="chart-title">状态说明</span>
          </template>
          <div class="status-legend">
            <div v-for="item in statusLegend" :key="item.key" class="status-legend__item">
              <span class="status-legend__dot" :style="{ background: item.color }"></span>
              <span class="status-legend__label">{{ item.label }}</span>
              <span class="status-legend__count">{{ summary.byStatus[item.key] ?? 0 }}</span>
            </div>
          </div>
        </el-card>
      </template>

      <!-- Department Tab -->
      <template v-if="activeTab === 'department'">
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">部门资产分布（Top 10）</span>
              <el-select v-model="deptChartType" size="small" style="width: 120px">
                <el-option label="柱状图" value="bar" />
                <el-option label="饼图" value="pie" />
              </el-select>
            </div>
          </template>
          <div ref="deptChartRef" class="chart-container" v-loading="chartsLoading" />
        </el-card>
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <span class="chart-title">部门明细</span>
          </template>
          <el-table :data="distribution.byDepartment" stripe size="small">
            <el-table-column prop="name" label="部门" />
            <el-table-column prop="value" label="资产数量" width="120" align="center" />
            <el-table-column label="占比" width="120" align="center">
              <template #default="{ row }">
                {{ summary.total > 0 ? ((row.value / summary.total) * 100).toFixed(1) : 0 }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>

      <!-- Importance Tab -->
      <template v-if="activeTab === 'importance'">
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">资产重要度分布</span>
              <el-select v-model="importanceChartType" size="small" style="width: 120px">
                <el-option label="饼图" value="pie" />
                <el-option label="柱状图" value="bar" />
              </el-select>
            </div>
          </template>
          <div ref="importanceChartRef" class="chart-container" v-loading="chartsLoading" />
        </el-card>
        <el-card class="chart-card chart-card--wide" v-if="distribution.byImportance.length === 0 && !chartsLoading">
          <el-empty description="暂无重要度数据，请先在资产中设置重要度等级">
            <template #image>
              <div style="font-size: 48px; text-align: center;">📭</div>
            </template>
            <el-button type="primary" size="small" @click="$router.push('/assets')">去管理资产</el-button>
          </el-empty>
        </el-card>
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <span class="chart-title">重要度明细</span>
          </template>
          <el-table :data="importanceTableData" stripe size="small">
            <el-table-column prop="name" label="重要度等级" />
            <el-table-column prop="value" label="资产数量" width="120" align="center" />
            <el-table-column label="占比" width="120" align="center">
              <template #default="{ row }">
                {{ summary.total > 0 ? ((row.value / summary.total) * 100).toFixed(1) : 0 }}%
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>

      <!-- Trend Tab -->
      <template v-if="activeTab === 'trend'">
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">近{{ trendMonths }}个月资产趋势</span>
              <el-select v-model="trendMonths" size="small" style="width: 120px" @change="fetchTrend">
                <el-option label="近6个月" :value="6" />
                <el-option label="近12个月" :value="12" />
                <el-option label="近24个月" :value="24" />
              </el-select>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container" v-loading="chartsLoading" />
        </el-card>
        <el-card class="chart-card chart-card--wide">
          <template #header>
            <span class="chart-title">趋势明细</span>
          </template>
          <el-table :data="trend" stripe size="small">
            <el-table-column prop="month" label="月份" width="120" />
            <el-table-column prop="added" label="本月新增" width="120" align="center">
              <template #default="{ row }">
                <span class="text-success">+{{ row.added }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="retired" label="本月报废" width="120" align="center">
              <template #default="{ row }">
                <span class="text-danger">-{{ row.retired }}</span>
              </template>
            </el-table-column>
            <el-table-column label="净增长" align="center">
              <template #default="{ row }">
                <span :class="row.added - row.retired >= 0 ? 'text-success' : 'text-danger'">
                  {{ row.added - row.retired >= 0 ? '+' : '' }}{{ row.added - row.retired }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useAssetStore } from '@/stores/assets'
import { reportsApi, type AssetSummary } from '@/api/reportsApi'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const assetStore = useAssetStore()

const summary = reactive<AssetSummary>({
  total: 0,
  byStatus: {},
  byCategory: [],
  byDepartment: [],
  byImportance: {},
  thisMonthNew: 0,
  thisMonthRetired: 0
})

const distribution = reactive({
  byCategory: [] as { name: string; value: number }[],
  byStatus: [] as { name: string; value: number }[],
  byDepartment: [] as { name: string; value: number }[],
  byImportance: [] as { name: string; value: number }[]
})

const trend = ref<{ month: string; added: number; retired: number }[]>([])

// Chart types per tab
const categoryChartType = ref<'pie' | 'bar'>('pie')
const deptChartType = ref<'bar' | 'pie'>('bar')
const importanceChartType = ref<'pie' | 'bar'>('pie')
const trendMonths = ref(6)

const activeTab = ref('category')

// Computed
const inUse = computed(() => summary.byStatus['in_use'] ?? 0)
const addedThisMonth = computed(() => summary.thisMonthNew)
const scrappedThisMonth = computed(() => summary.thisMonthRetired)

const importanceTableData = computed(() => {
  return distribution.byImportance.map(d => ({
    name: d.name === 'undefined' ? '未分类' : d.name,
    value: d.value
  }))
})

const statusLegend = [
  { key: 'in_use', label: '使用中', color: '#1AAD19' },
  { key: 'idle', label: '闲置', color: '#909399' },
  { key: 'maintenance', label: '维护中', color: '#FF991A' },
  { key: 'retired', label: '已退役', color: '#FA5151' },
  { key: 'scrapped', label: '已报废', color: '#C0C4CC' }
]

const dateRange = ref<string[]>([])
const chartsLoading = ref(false)

const filterParams = reactive({
  department_id: undefined as number | undefined,
  category_id: undefined as number | undefined
})

const departments = assetStore.departments
const categories = assetStore.categories

// Chart refs
const categoryChartRef = ref<HTMLElement | null>(null)
const statusChartRef = ref<HTMLElement | null>(null)
const deptChartRef = ref<HTMLElement | null>(null)
const importanceChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

// Chart instances
let categoryChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null
let deptChart: echarts.ECharts | null = null
let importanceChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

function getWechatColors() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark'
  return {
    text: isDark ? '#E0E0E0' : '#666666',
    splitLine: isDark ? '#3A3A3C' : '#E5E5E5',
    seriesColors: ['#1AAD19', '#FF991A', '#FA5151', '#07C160', '#909399', '#5470C6', '#FAC858', '#EE6666', '#73AC0D', '#3D8BF0']
  }
}

function getChartBaseOption() {
  const c = getWechatColors()
  return {
    textStyle: { color: c.text },
    tooltip: { trigger: 'item' }
  }
}

function makePieSeries(data: { name: string; value: number }[]) {
  const c = getWechatColors()
  return {
    type: 'pie' as const,
    radius: ['35%', '65%'],
    avoidLabelOverlap: true,
    itemStyle: { borderRadius: 6, borderColor: 'var(--bg-page)', borderWidth: 2 },
    label: { show: true, color: c.text, formatter: '{b}: {c} ({d}%)' },
    data: data.map((d, i) => ({
      ...d,
      itemStyle: { color: getWechatColors().seriesColors[i % getWechatColors().seriesColors.length] }
    }))
  }
}

function makeBarSeries(data: { name: string; value: number }[], horizontal = false) {
  const c = getWechatColors()
  const sorted = [...data].sort((a, b) => b.value - a.value)
  return {
    type: 'bar' as const,
    data: sorted.map((d, i) => ({
      value: d.value,
      itemStyle: { color: getWechatColors().seriesColors[i % getWechatColors().seriesColors.length] }
    })),
    barMaxWidth: 30,
    label: { show: true, position: horizontal ? 'right' : 'top', color: c.text },
    ...(horizontal ? {
      label: { show: true, position: 'right' as const, color: c.text }
    } : {})
  }
}

// ── Category Chart ──
function initCategoryChart() {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  const c = getWechatColors()
  if (categoryChartType.value === 'pie') {
    categoryChart.setOption({
      ...getChartBaseOption(),
      legend: { bottom: 0, textStyle: { color: c.text } },
      series: [makePieSeries(distribution.byCategory)]
    })
  } else {
    categoryChart.setOption({
      ...getChartBaseOption(),
      grid: { left: 120, right: 30, top: 10, bottom: 40 },
      xAxis: { type: 'category' as const, data: distribution.byCategory.map(d => d.name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: c.text, rotate: 30 } },
      yAxis: { type: 'value' as const, axisLine: { show: false }, splitLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text } },
      series: [makeBarSeries(distribution.byCategory)]
    })
  }
}

// ── Status Chart ──
function initStatusChart() {
  if (!statusChartRef.value) return
  statusChart = echarts.init(statusChartRef.value)
  const c = getWechatColors()
  const statusLabelMap: Record<string, string> = {
    in_use: '使用中', idle: '闲置', maintenance: '维护中', retired: '已退役', scrapped: '已报废'
  }
  const statusColors: Record<string, string> = {
    in_use: '#1AAD19', idle: '#909399', maintenance: '#FF991A', retired: '#FA5151', scrapped: '#C0C4CC'
  }
  const data = distribution.byStatus.map(d => ({
    name: statusLabelMap[d.name] || d.name,
    value: d.value,
    itemStyle: { color: statusColors[d.name] || '#909399' }
  }))
  statusChart.setOption({
    ...getChartBaseOption(),
    legend: { bottom: 0, textStyle: { color: c.text } },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: 'var(--bg-page)', borderWidth: 2 },
      label: { show: true, color: c.text },
      data
    }]
  })
}

// ── Department Chart ──
function initDeptChart() {
  if (!deptChartRef.value) return
  deptChart = echarts.init(deptChartRef.value)
  const c = getWechatColors()
  const sorted = [...distribution.byDepartment].sort((a, b) => b.value - a.value).slice(0, 10)
  if (deptChartType.value === 'pie') {
    deptChart.setOption({
      ...getChartBaseOption(),
      legend: { bottom: 0, textStyle: { color: c.text } },
      series: [makePieSeries(sorted)]
    })
  } else {
    deptChart.setOption({
      ...getChartBaseOption(),
      grid: { left: 120, right: 30, top: 10, bottom: 60 },
      xAxis: { type: 'category' as const, data: sorted.map(d => d.name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: c.text, rotate: 30 } },
      yAxis: { type: 'value' as const, axisLine: { show: false }, splitLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text } },
      series: [makeBarSeries(sorted)]
    })
  }
}

// ── Importance Chart ──
function initImportanceChart() {
  if (!importanceChartRef.value) return
  importanceChart = echarts.init(importanceChartRef.value)
  const c = getWechatColors()
  const data = distribution.byImportance.map(d => ({
    name: d.name === 'undefined' ? '未分类' : d.name,
    value: d.value
  }))
  if (importanceChartType.value === 'pie') {
    importanceChart.setOption({
      ...getChartBaseOption(),
      legend: { bottom: 0, textStyle: { color: c.text } },
      series: [makePieSeries(data)]
    })
  } else {
    importanceChart.setOption({
      ...getChartBaseOption(),
      grid: { left: 120, right: 30, top: 10, bottom: 40 },
      xAxis: { type: 'category' as const, data: data.map(d => d.name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: c.text, rotate: 30 } },
      yAxis: { type: 'value' as const, axisLine: { show: false }, splitLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text } },
      series: [makeBarSeries(data)]
    })
  }
}

// ── Trend Chart ──
function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const c = getWechatColors()
  const months = trend.value.map(t => t.month)
  const addedData = trend.value.map(t => t.added)
  const retiredData = trend.value.map(t => t.retired)
  trendChart.setOption({
    ...getChartBaseOption(),
    grid: { left: 50, right: 20, top: 10, bottom: 40 },
    legend: { bottom: 0, textStyle: { color: c.text } },
    xAxis: {
      type: 'category' as const,
      data: months,
      axisLine: { lineStyle: { color: c.splitLine } },
      axisLabel: { color: c.text },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value' as const,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: c.splitLine } },
      axisLabel: { color: c.text }
    },
    series: [
      {
        name: '新增',
        type: 'line' as const,
        data: addedData,
        smooth: true,
        lineStyle: { color: '#1AAD19', width: 2 },
        itemStyle: { color: '#1AAD19' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(26, 173, 25, 0.3)' }, { offset: 1, color: 'rgba(26, 173, 25, 0.02)' }]) },
        symbol: 'circle',
        symbolSize: 6
      },
      {
        name: '报废',
        type: 'line' as const,
        data: retiredData,
        smooth: true,
        lineStyle: { color: '#FA5151', width: 2 },
        itemStyle: { color: '#FA5151' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(250, 81, 81, 0.2)' }, { offset: 1, color: 'rgba(250, 81, 81, 0.02)' }]) },
        symbol: 'circle',
        symbolSize: 6
      }
    ]
  })
}

function resizeCharts() {
  categoryChart?.resize()
  statusChart?.resize()
  deptChart?.resize()
  importanceChart?.resize()
  trendChart?.resize()
}

// Re-init chart when tab or chart type changes
function onTabChange(tab: string) {
  setTimeout(() => {
    if (tab === 'category') initCategoryChart()
    else if (tab === 'status') initStatusChart()
    else if (tab === 'department') initDeptChart()
    else if (tab === 'importance') initImportanceChart()
    else if (tab === 'trend') initTrendChart()
  }, 50)
}

// Watch chart type changes
watch(categoryChartType, () => initCategoryChart())
watch(deptChartType, () => initDeptChart())
watch(importanceChartType, () => initImportanceChart())

async function fetchSummary() {
  try {
    const params: Record<string, any> = {}
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await reportsApi.assetSummary(params)
    Object.assign(summary, res.data)
  } catch {
    // ignore
  }
}

async function fetchDistribution() {
  chartsLoading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterParams.department_id) params.department_id = filterParams.department_id
    if (filterParams.category_id) params.category_id = filterParams.category_id
    const res = await reportsApi.assetDistribution(params)
    distribution.byCategory = res.data.byCategory
    distribution.byStatus = res.data.byStatus
    distribution.byDepartment = res.data.byDepartment
    distribution.byImportance = res.data.byImportance
    onTabChange(activeTab.value)
  } catch {
    // ignore
  } finally {
    chartsLoading.value = false
  }
}

async function fetchTrend() {
  try {
    const res = await reportsApi.assetTrend({ months: trendMonths.value })
    trend.value = res.data.items
    if (activeTab.value === 'trend') initTrendChart()
  } catch {
    // ignore
  }
}

async function fetchAll() {
  await Promise.all([fetchSummary(), fetchDistribution(), fetchTrend()])
}

function onDateChange() {
  fetchSummary()
}

function resetFilters() {
  dateRange.value = []
  filterParams.department_id = undefined
  filterParams.category_id = undefined
  fetchAll()
}

function exportCsv() {
  const headers = ['月份', '资产总数', '本月新增', '本月报废']
  const rows = [[
    dayjs().format('YYYY-MM'),
    summary.total,
    summary.thisMonthNew,
    summary.thisMonthRetired
  ]]
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `asset_report_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
  ElMessage.success('报表已导出')
}

onMounted(async () => {
  try {
    await assetStore.fetchOptions().catch(() => {})
    await fetchAll().catch(() => {})
    window.addEventListener('resize', resizeCharts)
  } catch (e) { /* ignore */ }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  categoryChart?.dispose()
  statusChart?.dispose()
  deptChart?.dispose()
  importanceChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.reports-page {
  max-width: 1400px;
  margin: 0 auto;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.summary-card {
  border-radius: var(--radius-lg) !important;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 4px 0;
}

.summary-card__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.summary-card__icon--primary { background: rgba(26, 173, 25, 0.1); color: #1AAD19; }
.summary-card__icon--success { background: rgba(7, 193, 96, 0.1); color: #07C160; }
.summary-card__icon--danger  { background: rgba(250, 81, 81, 0.1); color: #FA5151; }
.summary-card__icon--info    { background: rgba(144, 147, 153, 0.1); color: #909399; }

.summary-card__content {
  flex: 1;
}

.summary-card__value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.summary-card__label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.filter-card {
  margin-bottom: 16px;
  border-radius: var(--radius-lg) !important;
}

.tab-card {
  margin-bottom: 16px;
  border-radius: var(--radius-lg) !important;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  border-radius: var(--radius-lg) !important;
}

.chart-card--wide {
  grid-column: span 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-container {
  height: 280px;
  width: 100%;
}

.status-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 8px 0;
}

.status-legend__item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-legend__dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-legend__label {
  color: var(--text-secondary);
  font-size: 13px;
}

.status-legend__count {
  font-weight: 600;
  color: var(--text-primary);
}

.text-success { color: #1AAD19; font-weight: 600; }
.text-danger  { color: #FA5151; font-weight: 600; }

@media (max-width: 1024px) {
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
  .chart-card--wide { grid-column: span 1; }
}

@media (max-width: 640px) {
  .summary-cards { grid-template-columns: 1fr 1fr; }
  .summary-card__value { font-size: 20px; }
}

@media (max-width: 480px) {
  .reports-page { padding: 8px; }
  .summary-cards { grid-template-columns: 1fr 1fr !important; gap: 8px !important; }
  .summary-card { padding: 12px 8px !important; }
  .summary-card__value { font-size: 18px !important; }
}
</style>
