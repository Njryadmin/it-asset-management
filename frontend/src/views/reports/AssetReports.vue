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

    <!-- Charts Grid -->
    <div class="charts-grid anim-fade-in-up">
      <el-card class="chart-card chart-card--wide">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">资产分类分布</span>
          </div>
        </template>
        <div ref="categoryChartRef" class="chart-container" v-loading="chartsLoading" />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">资产状态分布</span>
          </div>
        </template>
        <div ref="statusChartRef" class="chart-container" v-loading="chartsLoading" />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">部门资产分布</span>
          </div>
        </template>
        <div ref="deptChartRef" class="chart-container" v-loading="chartsLoading" />
      </el-card>

      <el-card class="chart-card chart-card--wide">
        <template #header>
          <div class="chart-header">
            <span class="chart-title">近6个月资产趋势</span>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-container" v-loading="chartsLoading" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
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
  byDepartment: [] as { name: string; value: number }[]
})

const trend = ref<{ month: string; added: number; retired: number }[]>([])

// Computed for template
const inUse = computed(() => summary.byStatus['in_use'] ?? 0)
const addedThisMonth = computed(() => summary.thisMonthNew)
const scrappedThisMonth = computed(() => summary.thisMonthRetired)

const dateRange = ref<string[]>([])
const chartsLoading = ref(false)

const filterParams = reactive({
  department_id: undefined as number | undefined,
  category_id: undefined as number | undefined
})

const departments = assetStore.departments
const categories = assetStore.categories

const categoryChartRef = ref<HTMLElement | null>(null)
const statusChartRef = ref<HTMLElement | null>(null)
const deptChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

let categoryChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null
let deptChart: echarts.ECharts | null = null
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

function initCategoryChart() {
  if (!categoryChartRef.value) return
  categoryChart = echarts.init(categoryChartRef.value)
  const c = getWechatColors()
  categoryChart.setOption({
    ...getChartBaseOption(),
    legend: { bottom: 0, textStyle: { color: c.text } },
    series: [{
      type: 'pie',
      radius: ['35%', '65%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: 'var(--wechat-bg)', borderWidth: 2 },
      label: { show: true, color: c.text },
      data: distribution.byCategory
    }]
  })
}

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
      itemStyle: { borderRadius: 6, borderColor: 'var(--wechat-bg)', borderWidth: 2 },
      label: { show: true, color: c.text },
      data
    }]
  })
}

function initDeptChart() {
  if (!deptChartRef.value) return
  deptChart = echarts.init(deptChartRef.value)
  const c = getWechatColors()
  const sorted = [...distribution.byDepartment].sort((a, b) => b.value - a.value).slice(0, 10)
  deptChart.setOption({
    ...getChartBaseOption(),
    grid: { left: 80, right: 30, top: 10, bottom: 40 },
    xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text } },
    yAxis: { type: 'category', data: sorted.map(d => d.name), axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: c.text, fontSize: 12 } },
    series: [{
      type: 'bar',
      data: sorted.map((d, i) => ({ value: d.value, itemStyle: { color: getWechatColors().seriesColors[i % getWechatColors().seriesColors.length] } })),
      barMaxWidth: 30,
      itemStyle: { borderRadius: [0, 4, 4, 0] }
    }]
  })
}

function initTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const c = getWechatColors()
  const months = trend.value.map(t => t.month)
  const addedData = trend.value.map(t => t.added)
  trendChart.setOption({
    ...getChartBaseOption(),
    grid: { left: 50, right: 20, top: 10, bottom: 40 },
    xAxis: { type: 'category', data: months, axisLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: c.splitLine } }, axisLabel: { color: c.text } },
    series: [{
      type: 'line',
      data: addedData,
      smooth: true,
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(26, 173, 25, 0.3)' }, { offset: 1, color: 'rgba(26, 173, 25, 0.02)' }]) },
      lineStyle: { color: '#1AAD19', width: 2 },
      itemStyle: { color: '#1AAD19' },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

function resizeCharts() {
  categoryChart?.resize()
  statusChart?.resize()
  deptChart?.resize()
  trendChart?.resize()
}

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
    initCategoryChart()
    initStatusChart()
    initDeptChart()
  } catch {
    // ignore
  } finally {
    chartsLoading.value = false
  }
}

async function fetchTrend() {
  try {
    const res = await reportsApi.assetTrend({ months: 6 })
    trend.value = res.data.items
    initTrendChart()
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
  await assetStore.fetchOptions()
  await fetchAll()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  categoryChart?.dispose()
  statusChart?.dispose()
  deptChart?.dispose()
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
  color: var(--wechat-text);
  line-height: 1.2;
}

.summary-card__label {
  font-size: 13px;
  color: var(--wechat-text-secondary);
  margin-top: 4px;
}

.filter-card {
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
  color: var(--wechat-text);
}

.chart-container {
  height: 260px;
  width: 100%;
}

@media (max-width: 1024px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-grid {
    grid-template-columns: 1fr;
  }
  .chart-card--wide {
    grid-column: span 1;
  }
}

@media (max-width: 640px) {
  .summary-cards {
    grid-template-columns: 1fr 1fr;
  }
  .summary-card__value {
    font-size: 20px;
  }
}
</style>
