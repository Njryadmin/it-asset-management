<template>
  <div class="department-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <el-button type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            新增部门
          </el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useDepartmentStore } from '@/stores/departments'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Department } from '@/types'

const departmentStore = useDepartmentStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)

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

onMounted(() => {
  departmentStore.fetchDepartments()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
