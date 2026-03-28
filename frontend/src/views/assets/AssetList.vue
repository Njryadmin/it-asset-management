<template>
  <div class="asset-list page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">资产管理</h3>
            <span class="item-count">共 {{ assetStore.total }} 条</span>
            <el-tag v-if="selectedAssets.length > 0" type="primary" size="small" class="selection-tag">
              已选择 {{ selectedAssets.length }} 项
            </el-tag>
          </div>
          <div class="header-actions" v-if="selectedAssets.length > 0">
            <el-button type="danger" @click="handleBatchDelete">
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedAssets.length }})
            </el-button>
            <el-button type="warning" @click="showBatchTransferDialog = true">
              <el-icon><RefreshRight /></el-icon>
              批量转移
            </el-button>
          </div>
          <div class="header-actions" v-else>
            <el-button @click="showFilterDrawer = true">
              <el-icon><Filter /></el-icon>
              筛选
            </el-button>
            <el-popover placement="bottom" :width="220" trigger="click">
              <template #reference>
                <el-button>
                  <el-icon><Setting /></el-icon>
                  字段
                </el-button>
              </template>
              <div class="column-settings">
                <div class="column-settings-header">
                  <span>列设置</span>
                  <el-button link type="primary" @click="resetToDefaults">重置</el-button>
                </div>
                <div class="column-settings-list">
                  <div
                    v-for="(col, index) in columns"
                    :key="col.key"
                    class="column-settings-item"
                    :class="{ 'is-dragging': draggingIndex === index }"
                    draggable="true"
                    @dragstart="onDragStart(index)"
                    @dragover="(e) => onDragOver(e, index)"
                    @dragend="onDragEnd"
                  >
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    <el-checkbox
                      :model-value="col.visible"
                      :disabled="!canHide(index)"
                      @change="toggleColumn(index)"
                    >{{ col.label }}</el-checkbox>
                  </div>
                </div>
              </div>
            </el-popover>
            <el-dropdown trigger="click" @command="handleExport">
              <el-button type="primary">
                <el-icon><Download /></el-icon>
                导出
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="filtered">
                    <el-icon><Filter /></el-icon>
                    导出筛选结果 ({{ assetStore.total }} 条)
                  </el-dropdown-item>
                  <el-dropdown-item command="all">
                    <el-icon><Download /></el-icon>
                    导出全部
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="primary" @click="$router.push('/assets/create')">
              <el-icon><Plus /></el-icon>
              新增资产
            </el-button>
          </div>
        </div>
      </template>

      <!-- Quick search -->
      <div class="search-bar">
        <el-input
          v-model="assetStore.params.keyword"
          placeholder="搜索名称/编号/序列号..."
          clearable
          class="search-input"
          @clear="search"
          @keyup.enter="search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <!-- Active filters tags -->
      <div v-if="hasActiveFilters" class="filter-tags">
        <el-tag v-if="assetStore.params.keyword" closable @close="clearKeyword">
          关键词: {{ assetStore.params.keyword }}
        </el-tag>
        <el-tag v-if="assetStore.params.category_id" closable @close="clearCategory">
          分类: {{ getCategoryName(assetStore.params.category_id) }}
        </el-tag>
        <el-tag v-if="assetStore.params.status" closable @close="clearStatus">
          状态: {{ statusMap[assetStore.params.status] }}
        </el-tag>
        <el-tag v-if="assetStore.params.region" closable @close="clearRegion">
          地区: {{ assetStore.params.region }}
        </el-tag>
        <el-button text type="primary" @click="resetFilters">清除全部</el-button>
      </div>

      <!-- Table -->
      <el-table :data="assetStore.assets" v-loading="assetStore.loading" style="width: 100%" class="data-table" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="45" />
        <template v-for="col in columns" :key="col.key">
          <el-table-column v-if="col.visible && col.key === 'name'" prop="name" label="资产名称" min-width="150">
            <template #default="{ row }">
              <router-link :to="`/assets/${row.id}`" class="asset-name-link">{{ row.name }}</router-link>
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'assetCode'" prop="assetCode" label="资产编号" width="140" />
          <el-table-column v-if="col.visible && col.key === 'serialNumber'" prop="serialNumber" label="序列号" width="140" />
          <el-table-column v-if="col.visible && col.key === 'category'" prop="categoryId" label="分类" width="120">
            <template #default="{ row }">
              {{ getCategoryName(row.categoryId) }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'supplier'" prop="supplierId" label="供应商" width="120">
            <template #default="{ row }">
              {{ getSupplierName(row.supplierId) }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'department'" prop="departmentId" label="部门" width="120">
            <template #default="{ row }">
              {{ getDepartmentName(row.departmentId) }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'assignedTo'" prop="assignedTo" label="使用人" width="100">
            <template #default="{ row }">
              {{ row.assignedTo || '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'status'" prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'purchasePrice'" prop="purchasePrice" label="购买价格" width="100">
            <template #default="{ row }">
              {{ row.purchasePrice ? `¥${row.purchasePrice}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'purchaseDate'" prop="purchaseDate" label="购买日期" width="120">
            <template #default="{ row }">
              {{ row.purchaseDate ? dayjs(row.purchaseDate).format('YYYY-MM-DD') : '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'warrantyExpireDate'" prop="warrantyExpireDate" label="保修到期" width="120">
            <template #default="{ row }">
              {{ row.warrantyExpireDate ? dayjs(row.warrantyExpireDate).format('YYYY-MM-DD') : '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'description'" prop="description" label="备注" min-width="150" show-overflow-tooltip />
          <el-table-column v-if="col.visible && col.key === 'region'" prop="region" label="地区" width="120" />
          <el-table-column v-if="col.visible && col.key === 'createdAt'" prop="createdAt" label="添加时间" width="160">
            <template #default="{ row }">
              {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
            </template>
          </el-table-column>
        </template>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <span class="action-link" @click="$router.push(`/assets/${row.id}/edit`)">
              <el-icon><Edit /></el-icon>
              <span>编辑</span>
            </span>
            <span class="action-link action-link--danger" @click="handleDelete(row.id)">
              <el-icon><Delete /></el-icon>
              <span>删除</span>
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="assetStore.params.page"
          :page-size="assetStore.params.page_size"
          :total="assetStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Filter Drawer -->
    <el-drawer v-model="showFilterDrawer" title="筛选条件" direction="rtl" size="300px">
      <el-form label-width="80px">
        <el-form-item label="关键词">
          <el-input v-model="tempParams.keyword" placeholder="搜索名称/编号/序列号" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="tempParams.category_id" placeholder="选择分类" clearable style="width: 100%">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="tempParams.status" placeholder="选择状态" clearable style="width: 100%">
            <el-option label="使用中" value="in_use" />
            <el-option label="闲置" value="idle" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="retired" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="tempParams.department_id" placeholder="选择部门" clearable style="width: 100%">
            <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="tempParams.region" placeholder="输入地区" clearable style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="resetTempParams">重置</el-button>
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- Import Dialog -->
    <el-dialog v-model="showImportDialog" title="导入资产" width="90%" max-width="500px" class="custom-dialog">
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :action="importUrl"
        :headers="{ Authorization: `Bearer ${token}` }"
        :before-upload="beforeUpload"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
        accept=".csv"
        :auto-upload="false"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽CSV文件到此处 或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只能上传CSV文件，请先下载模板</div>
          <el-button size="small" type="primary" @click="downloadTemplate">下载模板</el-button>
        </template>
      </el-upload>
      <template #footer>
        <el-button type="primary" @click="submitImport">确定导入</el-button>
        <el-button @click="showImportDialog = false">取消</el-button>
      </template>
    </el-dialog>
  </div>

  <!-- Batch Transfer Dialog -->
  <el-dialog v-model="showBatchTransferDialog" title="批量转移资产" width="500px" class="custom-dialog">
    <el-form :model="batchTransferForm" label-width="100px">
      <el-form-item label="目标部门">
        <el-select v-model="batchTransferForm.departmentId" placeholder="选择部门" clearable filterable>
          <el-option v-for="dept in departmentStore.departments" :key="dept.id" :label="dept.name" :value="dept.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="目标使用人">
        <el-select v-model="batchTransferForm.userId" placeholder="选择使用人" clearable filterable>
          <el-option v-for="user in userStore.users" :key="user.id" :label="user.fullName || user.username" :value="user.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="转移原因">
        <el-input v-model="batchTransferForm.reason" type="textarea" :rows="2" placeholder="请输入转移原因" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showBatchTransferDialog = false">取消</el-button>
      <el-button type="primary" @click="confirmBatchTransfer" :loading="batchTransferLoading">确认转移</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { useDepartmentStore } from '@/stores/departments'
import { useUserStore } from '@/stores/users'
import { assetsApi } from '@/api/assets'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useColumnSettings } from '@/composables/useColumnSettings'
import type { ColumnOption } from '@/composables/useColumnSettings'
import type { Asset } from '@/types'
import dayjs from 'dayjs'

const defaultColumns: ColumnOption[] = [
  { key: 'name', label: '资产名称', visible: true },
  { key: 'assetCode', label: '资产编号', visible: true },
  { key: 'serialNumber', label: '序列号', visible: true },
  { key: 'category', label: '分类', visible: true },
  { key: 'supplier', label: '供应商', visible: true },
  { key: 'department', label: '部门', visible: true },
  { key: 'assignedTo', label: '使用人', visible: true },
  { key: 'status', label: '状态', visible: true },
  { key: 'purchasePrice', label: '购买价格', visible: true },
  { key: 'purchaseDate', label: '购买日期', visible: true },
  { key: 'warrantyExpireDate', label: '保修到期', visible: false },
  { key: 'description', label: '备注', visible: false },
  { key: 'region', label: '地区', visible: true },
  { key: 'createdAt', label: '添加时间', visible: true }
]

const {
  columns,
  draggingIndex,
  onDragStart,
  onDragOver,
  onDragEnd,
  toggleColumn,
  canHide,
  resetToDefaults
} = useColumnSettings('asset-columns', defaultColumns)

const router = useRouter()
const assetStore = useAssetStore()
const departmentStore = useDepartmentStore()
const userStore = useUserStore()
const token = localStorage.getItem('token') || ''
const importUrl = '/api/v1/assets/import'
const uploadRef = ref()
const showImportDialog = ref(false)
const selectedAssets = ref<Asset[]>([])
const showBatchTransferDialog = ref(false)
const batchTransferLoading = ref(false)
const batchTransferForm = reactive({
  departmentId: null as number | null,
  userId: null as number | null,
  reason: ''
})
const showFilterDrawer = ref(false)

// Legacy reference - table now uses 'columns' from composable
const columnOptions = ref(defaultColumns)

const tempParams = reactive({
  keyword: '',
  category_id: undefined as number | undefined,
  status: '',
  department_id: undefined as number | undefined,
  region: ''
})

const flatCategories = computed(() => {
  const result: any[] = []
  function flatten(cats: any[], level = 0) {
    for (const cat of cats) {
      result.push({ ...cat, level })
      if (cat.children?.length) {
        flatten(cat.children, level + 1)
      }
    }
  }
  flatten(assetStore.categories)
  return result
})

const flatDepartments = computed(() => {
  const result: any[] = []
  function flatten(depts: any[], level = 0) {
    for (const dept of depts) {
      result.push({ ...dept, level })
      if (dept.children?.length) {
        flatten(dept.children, level + 1)
      }
    }
  }
  flatten(assetStore.departments)
  return result
})

const hasActiveFilters = computed(() => {
  return assetStore.params.keyword || assetStore.params.category_id || assetStore.params.status || assetStore.params.department_id || assetStore.params.region
})

const statusMap: Record<string, string> = {
  in_use: '使用中',
  idle: '闲置',
  maintenance: '维护中',
  retired: '已退役',
  scrapped: '已报废'
}

function statusLabel(status: string) {
  return statusMap[status] || status
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

function handleSelectionChange(selection: Asset[]) {
  selectedAssets.value = selection
}

async function handleBatchDelete() {
  const count = selectedAssets.value.length
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${count} 项资产吗？此操作不可恢复。`,
      '批量删除确认',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    const ids = selectedAssets.value.map(a => a.id)
    await assetsApi.batchDelete(ids)
    ElMessage.success(`成功删除 ${count} 项资产`)
    selectedAssets.value = []
    await assetStore.fetchAssets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

async function confirmBatchTransfer() {
  if (!batchTransferForm.departmentId && !batchTransferForm.userId) {
    ElMessage.warning('请至少选择目标部门或目标使用人')
    return
  }
  batchTransferLoading.value = true
  try {
    const ids = selectedAssets.value.map(a => a.id)
    await assetsApi.batchTransfer({
      asset_ids: ids,
      to_department_id: batchTransferForm.departmentId || undefined,
      to_user_id: batchTransferForm.userId || undefined,
      reason: batchTransferForm.reason || undefined
    })
    ElMessage.success(`成功转移 ${ids.length} 项资产`)
    showBatchTransferDialog.value = false
    selectedAssets.value = []
    batchTransferForm.departmentId = null
    batchTransferForm.userId = null
    batchTransferForm.reason = ''
    await assetStore.fetchAssets()
  } catch (error) {
    ElMessage.error('批量转移失败')
  } finally {
    batchTransferLoading.value = false
  }
}

function handleActionCommand(cmd: string, row: any) {
  if (cmd === 'delete') handleDelete(row.id)
}

function getCategoryName(id: number | null) {
  if (!id) return '-'
  const cat = flatCategories.value.find(c => c.id === id)
  return cat?.name || '-'
}

function getSupplierName(id: number | null) {
  if (!id) return '-'
  const sup = assetStore.suppliers.find(s => s.id === id)
  return sup?.name || '-'
}

function getDepartmentName(id: number | null) {
  if (!id) return '-'
  const dept = flatDepartments.value.find(d => d.id === id)
  return dept?.name || '-'
}

async function search() {
  assetStore.params.page = 1
  await assetStore.fetchAssets()
}

async function reset() {
  assetStore.resetParams()
  await assetStore.fetchAssets()
}

async function handlePageChange(page: number) {
  assetStore.params.page = page
  await assetStore.fetchAssets()
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条资产记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await assetStore.deleteAsset(id)
    ElMessage.success('删除成功')
    await assetStore.fetchAssets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function clearKeyword() {
  assetStore.params.keyword = ''
  search()
}

function clearCategory() {
  assetStore.params.category_id = undefined
  search()
}

function clearStatus() {
  assetStore.params.status = ''
  search()
}

function clearRegion() {
  assetStore.params.region = ''
  search()
}

function resetFilters() {
  reset()
}

function resetTempParams() {
  tempParams.keyword = ''
  tempParams.category_id = undefined
  tempParams.status = ''
  tempParams.department_id = undefined
  tempParams.region = ''
}

function applyFilters() {
  assetStore.params.keyword = tempParams.keyword
  assetStore.params.category_id = tempParams.category_id
  assetStore.params.status = tempParams.status
  assetStore.params.department_id = tempParams.department_id
  assetStore.params.region = tempParams.region
  showFilterDrawer.value = false
  search()
}

async function handleExport(command: string) {
  try {
    const params: Record<string, any> = {}
    let filename = `assets_all_${dayjs().format('YYYYMMDD_HHmmss')}`
    
    if (command === 'filtered') {
      if (assetStore.params.keyword) params.keyword = assetStore.params.keyword
      if (assetStore.params.category_id) params.category_id = assetStore.params.category_id
      if (assetStore.params.status) params.status = assetStore.params.status
      if (assetStore.params.department_id) params.department_id = assetStore.params.department_id
      if (assetStore.params.region) params.region = assetStore.params.region
      filename = `assets_filtered_${dayjs().format('YYYYMMDD_HHmmss')}`
    }
    
    await assetsApi.exportFile(Object.keys(params).length > 0 ? params : undefined, `${filename}.csv`)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

function beforeUpload(file: any) {
  const isCSV = file.name.endsWith('.csv')
  if (!isCSV) {
    ElMessage.error('只能上传CSV文件')
  }
  return isCSV
}

function handleImportSuccess(response: any) {
  if (response.imported !== undefined) {
    ElMessage.success(`导入完成：成功${response.imported}条，跳过${response.skipped}条`)
    showImportDialog.value = false
    assetStore.fetchAssets()
  }
}

function handleImportError(error: any) {
  ElMessage.error('导入失败')
}

function submitImport() {
  uploadRef.value?.submit()
}

function downloadTemplate() {
  const template = '\ufeff资产编号,名称,序列号,分类名称,供应商名称,部门名称,使用人,状态,购入日期,购入价格,保修期至,描述,规格参数,地区\n'
  const code = 'CODE001,示例资产,SN123456,1,,1,,idle,2024-01-01,5000.00,2026-01-01,示例描述,示例规格,上海'
  const blob = new Blob([template + code], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'asset_template.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

onMounted(async () => {
  await assetStore.fetchOptions()
  await assetStore.fetchAssets()
  await departmentStore.fetchDepartments()
  await userStore.fetchUsers()
})
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.main-card {
  border-radius: var(--radius-lg) !important;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 14px 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--wechat-text);
}

.item-count {
  font-size: 13px;
  color: var(--wechat-text-secondary);
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}

.filter-tags {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.data-table {
  border-radius: 0;
  overflow-x: auto;
}

.data-table :deep(.el-table__body-wrapper) {
  overflow-x: auto !important;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.custom-dialog :deep(.el-dialog) {
  border-radius: var(--radius-lg) !important;
}

.upload-demo {
  text-align: center;
}

.column-settings {
  user-select: none;
}

.column-settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
  font-weight: 600;
}

.column-settings-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.column-settings-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: grab;
  transition: background-color 0.2s;
}

.column-settings-item:hover {
  background-color: var(--el-fill-color-light);
}

.column-settings-item.is-dragging {
  opacity: 0.5;
  background-color: var(--el-fill-color);
}

.drag-handle {
  color: var(--el-text-color-placeholder);
  cursor: grab;
}

@media (max-width: 768px) {
  .card-header {
    padding: 10px 12px;
  }
  .search-bar {
    margin-bottom: 12px;
  }
  .search-input {
    min-width: 0;
    max-width: 100%;
  }
  .el-table {
    font-size: 13px;
  }
  .el-table :deep(.el-table__header th),
  .el-table :deep(.el-table__body td) {
    padding: 8px 4px;
  }
  .el-table :deep(.el-table__cell) {
    min-width: 80px;
  }
  .el-table :deep(.el-button) {
    padding: 4px 6px;
  }
}

.asset-name-link {
  color: var(--wechat-primary);
  text-decoration: none;
  font-weight: 500;
}
.asset-name-link:hover {
  text-decoration: underline;
}
</style>
