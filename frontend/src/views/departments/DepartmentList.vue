<template>
  <div class="department-list page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">部门管理</h3>
            <span class="item-count">共 {{ departmentStore.total }} 条</span>
          </div>
          <div class="header-actions">
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
              <el-button>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="all">导出全部</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="primary" @click="showDialog('create')">
              <el-icon><Plus /></el-icon>
              新增部门
            </el-button>
          </div>
        </div>
      </template>

      <!-- Search -->
      <div class="search-bar">
        <el-input
          v-model="departmentStore.params.keyword"
          placeholder="搜索部门名称..."
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

      <!-- Tree Table -->
      <el-table :data="flatDepartments" v-loading="departmentStore.loading" row-key="id" style="width: 100%" class="data-table">
        <template v-for="col in columns" :key="col.key">
          <el-table-column v-if="col.visible && col.key === 'name'" prop="name" label="部门名称" min-width="200" />
          <el-table-column v-if="col.visible && col.key === 'code'" prop="code" label="编码" width="120" />
          <el-table-column v-if="col.visible && col.key === 'description'" prop="description" label="描述" min-width="200" show-overflow-tooltip />
        </template>
        <el-table-column label="操作" width="110" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog('edit', row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-dropdown trigger="click" @command="(cmd: string) => handleActionCommand(cmd, row)">
              <el-button type="primary" link>
                <el-icon><More /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="delete" style="color: #f56c6c">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="departmentStore.params.page"
          :page-size="departmentStore.params.page_size"
          :total="departmentStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="custom-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="form.parent_id" placeholder="请选择上级部门" clearable style="width: 100%">
            <el-option v-for="dept in selectableDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog v-model="showImportDialog" title="导入部门" width="500px" class="custom-dialog">
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useDepartmentStore } from '@/stores/departments'
import { departmentsApi } from '@/api/departments'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Department } from '@/types'
import { useColumnSettings } from '@/composables/useColumnSettings'
import type { ColumnOption } from '@/composables/useColumnSettings'
import dayjs from 'dayjs'

const defaultColumns: ColumnOption[] = [
  { key: 'name', label: '部门名称', visible: true },
  { key: 'code', label: '编码', visible: true },
  { key: 'description', label: '描述', visible: true }
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
} = useColumnSettings('department-columns', defaultColumns)

const departmentStore = useDepartmentStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)
const token = localStorage.getItem('token') || ''
const importUrl = '/api/v1/departments/import'
const uploadRef = ref()
const showImportDialog = ref(false)

const form = reactive({
  name: '',
  code: '',
  parent_id: undefined as number | undefined,
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增部门' : '编辑部门')

function handleActionCommand(cmd: string, row: Department) {
  if (cmd === 'delete') handleDelete(row.id)
}

const flatDepartments = computed(() => {
  const result: any[] = []
  function flatten(depts: Department[], level = 0) {
    for (const dept of depts) {
      result.push({ ...dept, level })
      if (dept.children?.length) {
        flatten(dept.children, level + 1)
      }
    }
  }
  flatten(departmentStore.departments)
  return result
})

// Get selectable parent departments (exclude self and descendants when editing)
const selectableDepartments = computed(() => {
  if (dialogMode.value === 'create' || !currentId.value) {
    return flatDepartments.value
  }
  // Collect IDs of current department and all its descendants
  const excludeIds = new Set<number>()
  function collectIds(dept: Department) {
    excludeIds.add(dept.id)
    dept.children?.forEach(child => collectIds(child))
  }
  const currentDept = flatDepartments.value.find(d => d.id === currentId.value)
  if (currentDept) collectIds(currentDept)
  return flatDepartments.value.filter(d => !excludeIds.has(d.id))
})

function showDialog(mode: 'create' | 'edit', data?: Department) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    Object.assign(form, {
      name: '',
      code: '',
      parent_id: undefined,
      description: ''
    })
  } else {
    currentId.value = data!.id
    Object.assign(form, {
      name: data!.name,
      code: data!.code || '',
      parent_id: data!.parentId,
      description: data!.description || ''
    })
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (dialogMode.value === 'create') {
          await departmentStore.createDepartment(form as any)
          ElMessage.success('创建成功')
        } else {
          await departmentStore.updateDepartment(currentId.value!, form as any)
          ElMessage.success('保存成功')
        }
        dialogVisible.value = false
      } catch (error) {
        // Error handled by interceptor
      } finally {
        loading.value = false
      }
    }
  })
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该部门吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await departmentStore.deleteDepartment(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handlePageChange(page: number) {
  departmentStore.params.page = page
  await departmentStore.fetchDepartments()
}

async function search() {
  departmentStore.params.page = 1
  await departmentStore.fetchDepartments()
}

async function reset() {
  departmentStore.params.keyword = ''
  departmentStore.params.page = 1
  await departmentStore.fetchDepartments()
}

async function handleExport(command: string) {
  try {
    const response = await fetch('/api/v1/departments/export', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `departments_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
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
    departmentStore.fetchDepartments()
  }
}

function handleImportError(error: any) {
  ElMessage.error('导入失败')
}

function submitImport() {
  uploadRef.value?.submit()
}

function downloadTemplate() {
  const template = '\ufeff部门名称,编码,上级部门ID,描述\n'
  const example = '研发部,RD,,研发部门\n测试部,QA,,测试部门'
  const blob = new Blob([template + example], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'department_template.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  departmentStore.fetchDepartments()
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
</style>
