<template>
  <div class="asset-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产管理</span>
          <div class="header-actions">
            <el-button @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
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

      <!-- Search filters -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="assetStore.params.keyword" placeholder="搜索名称/编号/序列号" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="assetStore.params.category_id" placeholder="选择分类" clearable @change="search">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="assetStore.params.status" placeholder="选择状态" clearable @change="search">
            <el-option label="使用中" value="in_use" />
            <el-option label="闲置" value="idle" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="retired" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table :data="assetStore.assets" v-loading="assetStore.loading" style="width: 100%">
        <el-table-column prop="name" label="资产名称" min-width="150" />
        <el-table-column prop="assetCode" label="资产编号" width="140" />
        <el-table-column prop="serialNumber" label="序列号" width="140" />
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
        <el-table-column prop="purchaseDate" label="购买日期" width="120">
          <template #default="{ row }">
            {{ row.purchaseDate ? dayjs(row.purchaseDate).format('YYYY-MM-DD') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="添加时间" width="160">
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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import request from '@/api/request'

const router = useRouter()
const assetStore = useAssetStore()
const token = localStorage.getItem('token') || ''
const importUrl = '/api/v1/assets/import'
const uploadRef = ref()
const showImportDialog = ref(false)

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

async function handleExport() {
  try {
    const response = await fetch('/api/v1/assets/export', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `assets_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
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
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
