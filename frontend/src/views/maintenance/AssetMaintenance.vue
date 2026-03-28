<template>
  <div class="maintenance-page page-container">
    <div class="page-header">
      <h1 class="page-title">维保记录管理</h1>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增维保记录
      </el-button>
    </div>

    <!-- Filter Bar -->
    <el-card class="filter-card">
      <div class="filter-bar">
        <el-select
          v-model="filterParams.asset_id"
          placeholder="选择资产"
          clearable
          filterable
          style="width: 200px"
          @change="fetchLogs"
        >
          <el-option
            v-for="asset in assetStore.assets"
            :key="asset.id"
            :label="asset.name"
            :value="asset.id"
          />
        </el-select>
        <el-select v-model="filterParams.maintenance_type" placeholder="维保类型" clearable style="width: 140px" @change="fetchLogs">
          <el-option label="维修" value="维修" />
          <el-option label="保养" value="保养" />
          <el-option label="巡检" value="巡检" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          style="width: 260px"
          @change="fetchLogs"
        />
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="fetchLogs">刷新</el-button>
      </div>
    </el-card>

    <!-- Table -->
    <el-card class="table-card">
      <el-table :data="logs" v-loading="loading" stripe size="small">
        <el-table-column prop="asset_name" label="资产名称" min-width="160" />
        <el-table-column prop="maintenance_type" label="维保类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.maintenance_type)" size="small">
              {{ row.maintenance_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_date" label="维保日期" width="120" align="center" />
        <el-table-column prop="vendor" label="供应商" min-width="120" show-overflow-tooltip />
        <el-table-column prop="cost" label="费用" width="100" align="right">
          <template #default="{ row }">
            <span v-if="row.cost != null">¥{{ row.cost.toFixed(2) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="next_maintenance_date" label="下次维保日期" width="130" align="center">
          <template #default="{ row }">
            <span v-if="row.next_maintenance_date">{{ row.next_maintenance_date }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑维保记录' : '新增维保记录'"
      width="520px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="资产" prop="asset_id">
          <el-select
            v-model="form.asset_id"
            placeholder="请选择资产"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="asset in assetStore.assets"
              :key="asset.id"
              :label="asset.name"
              :value="asset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维保类型" prop="maintenance_type">
          <el-select v-model="form.maintenance_type" placeholder="请选择维保类型" style="width: 100%">
            <el-option label="维修" value="维修" />
            <el-option label="保养" value="保养" />
            <el-option label="巡检" value="巡检" />
          </el-select>
        </el-form-item>
        <el-form-item label="维保日期" prop="maintenance_date">
          <el-date-picker
            v-model="form.maintenance_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择维保日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="供应商" prop="vendor">
          <el-input v-model="form.vendor" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="费用" prop="cost">
          <el-input-number
            v-model="form.cost"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入费用"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="下次维保日期" prop="next_maintenance_date">
          <el-date-picker
            v-model="form.next_maintenance_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择下次维保日期（选填）"
            style="width: 100%"
            clearable
          />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息（选填）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAssetStore } from '@/stores/assets'
import { maintenanceApi, type MaintenanceLog, type MaintenanceLogForm } from '@/api/maintenanceApi'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const assetStore = useAssetStore()

const logs = ref<MaintenanceLog[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const dateRange = ref<string[]>([])

const filterParams = reactive({
  asset_id: undefined as number | undefined,
  maintenance_type: undefined as string | undefined
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive<MaintenanceLogForm>({
  asset_id: 0,
  maintenance_type: '',
  maintenance_date: '',
  vendor: '',
  cost: undefined,
  description: '',
  next_maintenance_date: ''
})

const formRules: FormRules = {
  asset_id: [{ required: true, message: '请选择资产', trigger: 'change' }],
  maintenance_type: [{ required: true, message: '请选择维保类型', trigger: 'change' }],
  maintenance_date: [{ required: true, message: '请选择维保日期', trigger: 'change' }]
}

function getTypeTagType(type: string): '' | 'success' | 'warning' | 'danger' {
  const map: Record<string, '' | 'success' | 'warning' | 'danger'> = {
    '维修': 'danger',
    '保养': 'success',
    '巡检': 'warning'
  }
  return map[type] || ''
}

async function fetchLogs() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (filterParams.asset_id) params.asset_id = filterParams.asset_id
    if (filterParams.maintenance_type) params.maintenance_type = filterParams.maintenance_type
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await maintenanceApi.list(params)
    logs.value = res.data.items
    pagination.total = res.data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filterParams.asset_id = undefined
  filterParams.maintenance_type = undefined
  dateRange.value = []
  pagination.page = 1
  fetchLogs()
}

function openCreateDialog() {
  isEditing.value = false
  editingId.value = null
  dialogVisible.value = true
}

function openEditDialog(row: MaintenanceLog) {
  isEditing.value = true
  editingId.value = row.id
  form.asset_id = row.asset_id
  form.maintenance_type = row.maintenance_type
  form.maintenance_date = row.maintenance_date
  form.vendor = row.vendor || ''
  form.cost = row.cost
  form.description = row.description || ''
  form.next_maintenance_date = row.next_maintenance_date || ''
  dialogVisible.value = true
}

function resetForm() {
  formRef.value?.resetFields()
  form.asset_id = 0
  form.maintenance_type = ''
  form.maintenance_date = ''
  form.vendor = ''
  form.cost = undefined
  form.description = ''
  form.next_maintenance_date = ''
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (isEditing.value && editingId.value !== null) {
        await maintenanceApi.update(editingId.value, form)
        ElMessage.success('维保记录已更新')
      } else {
        await maintenanceApi.create(form)
        ElMessage.success('维保记录已创建')
      }
      dialogVisible.value = false
      fetchLogs()
    } catch {
      // handled by interceptor
    } finally {
      submitLoading.value = false
    }
  })
}

async function handleDelete(row: MaintenanceLog) {
  try {
    await ElMessageBox.confirm(
      `确定要删除资产"${row.asset_name}"的维保记录吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
    await maintenanceApi.delete(row.id)
    ElMessage.success('维保记录已删除')
    fetchLogs()
  } catch {
    // user cancelled or error
  }
}

onMounted(async () => {
  await assetStore.fetchAssets()
  await fetchLogs()
})
</script>

<style scoped>
.maintenance-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
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

.table-card {
  border-radius: var(--radius-lg) !important;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0 4px;
}

.text-muted {
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .filter-bar {
    gap: 8px;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
