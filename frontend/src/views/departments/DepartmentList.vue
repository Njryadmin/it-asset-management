<template>
  <div class="department-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <div class="header-actions">
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
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="departmentStore.params.keyword" placeholder="搜索部门名称" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Tree Table -->
      <el-table :data="flatDepartments" v-loading="departmentStore.loading" row-key="id" style="width: 100%">
        <el-table-column prop="name" label="部门名称" min-width="200" />
        <el-table-column prop="code" label="编码" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog('edit', row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="form.parent_id" placeholder="请选择上级部门" clearable style="width: 100%">
            <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
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
    <el-dialog v-model="showImportDialog" title="导入部门" width="500px">
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
import dayjs from 'dayjs'

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

async function search() {
  departmentStore.params.page = 1
  await departmentStore.fetchDepartments()
}

async function reset() {
  departmentStore.params.keyword = ''
  departmentStore.params.page = 1
  await departmentStore.fetchDepartments()
}

async function handlePageChange(page: number) {
  departmentStore.params.page = page
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
.department-list,
.page-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-form {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-card {
  border-radius: var(--radius-lg) !important;
}
</style>
