<template>
  <div class="asset-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产管理</span>
          <div class="header-actions">
            <el-button @click="showFilterDrawer = true">
              <el-icon><Filter /></el-icon>
              筛选
            </el-button>
            <el-dropdown trigger="click" @command="handleColumnToggle">
              <el-button>
                <el-icon><Setting /></el-icon>
                字段
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="col in columnOptions" :key="col.key">
                    <el-checkbox v-model="col.visible" :label="col.label" />
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="assetStore.params.keyword" placeholder="搜索名称/编号/序列号" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

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
        <el-button text type="primary" @click="resetFilters">清除全部</el-button>
      </div>

      <!-- Table -->
      <el-table :data="assetStore.assets" v-loading="assetStore.loading" style="width: 100%">
        <el-table-column v-if="columnOptions.find(c => c.key === 'name')?.visible" prop="name" label="资产名称" min-width="150" />
        <el-table-column v-if="columnOptions.find(c => c.key === 'assetCode')?.visible" prop="assetCode" label="资产编号" width="140" />
        <el-table-column v-if="columnOptions.find(c => c.key === 'serialNumber')?.visible" prop="serialNumber" label="序列号" width="140" />
        <el-table-column v-if="columnOptions.find(c => c.key === 'category')?.visible" prop="categoryId" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryName(row.categoryId) }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'supplier')?.visible" prop="supplierId" label="供应商" width="120">
          <template #default="{ row }">
            {{ getSupplierName(row.supplierId) }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'department')?.visible" prop="departmentId" label="部门" width="120">
          <template #default="{ row }">
            {{ getDepartmentName(row.departmentId) }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'status')?.visible" prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'purchasePrice')?.visible" prop="purchasePrice" label="购买价格" width="100">
          <template #default="{ row }">
            {{ row.purchasePrice ? `¥${row.purchasePrice}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'purchaseDate')?.visible" prop="purchaseDate" label="购买日期" width="120">
          <template #default="{ row }">
            {{ row.purchaseDate ? dayjs(row.purchaseDate).format('YYYY-MM-DD') : '-' }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'warrantyExpireDate')?.visible" prop="warrantyExpireDate" label="保修到期" width="120">
          <template #default="{ row }">
            {{ row.warrantyExpireDate ? dayjs(row.warrantyExpireDate).format('YYYY-MM-DD') : '-' }}
          </template>
        </el-table-column>
        <el-table-column v-if="columnOptions.find(c => c.key === 'description')?.visible" prop="description" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column v-if="columnOptions.find(c => c.key === 'createdAt')?.visible" prop="createdAt" label="添加时间" width="160">
          <template #default="{ row }">
            {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/assets/${row.id}/edit`)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
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
      </el-form>
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="resetTempParams">重置</el-button>
          <el-button type="primary" @click="applyFilters">应用筛选</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- Import Dialog -->
    <el-dialog v-model="showImportDialog" title="导入资产" width="500px">
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
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="submitImport">确定导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()
const assetStore = useAssetStore()
const token = localStorage.getItem('token') || ''
const importUrl = '/api/v1/assets/import'
const uploadRef = ref()
const showImportDialog = ref(false)
const showFilterDrawer = ref(false)

// Column visibility options
const columnOptions = ref([
  { key: 'name', label: '资产名称', visible: true },
  { key: 'assetCode', label: '资产编号', visible: true },
  { key: 'serialNumber', label: '序列号', visible: true },
  { key: 'category', label: '分类', visible: true },
  { key: 'supplier', label: '供应商', visible: true },
  { key: 'department', label: '部门', visible: true },
  { key: 'status', label: '状态', visible: true },
  { key: 'purchasePrice', label: '购买价格', visible: true },
  { key: 'purchaseDate', label: '购买日期', visible: true },
  { key: 'warrantyExpireDate', label: '保修到期', visible: false },
  { key: 'description', label: '备注', visible: false },
  { key: 'createdAt', label: '添加时间', visible: true }
])

// Temp params for filter drawer
const tempParams = reactive({
  keyword: '',
  category_id: undefined as number | undefined,
  status: '',
  department_id: undefined as number | undefined
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
  return assetStore.params.keyword || assetStore.params.category_id || assetStore.params.status || assetStore.params.department_id
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

function handleColumnToggle() {
  // Column toggle is handled by v-model on checkbox
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

function resetFilters() {
  reset()
}

function resetTempParams() {
  tempParams.keyword = ''
  tempParams.category_id = undefined
  tempParams.status = ''
  tempParams.department_id = undefined
}

function applyFilters() {
  assetStore.params.keyword = tempParams.keyword
  assetStore.params.category_id = tempParams.category_id
  assetStore.params.status = tempParams.status
  assetStore.params.department_id = tempParams.department_id
  showFilterDrawer.value = false
  search()
}

async function handleExport(command: string) {
  try {
    let url = '/api/v1/assets/export'
    let filename = 'assets'
    
    if (command === 'filtered') {
      // Export with current filters
      const params = new URLSearchParams()
      if (assetStore.params.keyword) params.append('keyword', assetStore.params.keyword)
      if (assetStore.params.category_id) params.append('category_id', String(assetStore.params.category_id))
      if (assetStore.params.status) params.append('status', assetStore.params.status)
      if (assetStore.params.department_id) params.append('department_id', String(assetStore.params.department_id))
      url += '?' + params.toString()
      filename = `assets_filtered_${dayjs().format('YYYYMMDD_HHmmss')}`
    } else {
      // Export all
      filename = `assets_all_${dayjs().format('YYYYMMDD_HHmmss')}`
    }
    
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = `${filename}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
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
  const template = '\ufeff资产编号,名称,序列号,分类ID,供应商ID,部门ID,使用人ID,状态,购入日期,购入价格,保修期至,描述,规格参数\n'
  const code = 'CODE001,示例资产,SN123456,1,,1,,idle,2024-01-01,5000.00,2026-01-01,示例描述,示例规格'
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
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-form {
  margin-bottom: 16px;
}

.filter-tags {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
