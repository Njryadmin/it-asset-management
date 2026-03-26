<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <!-- Search -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="userStore.params.keyword" placeholder="搜索用户名/邮箱/姓名" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table :data="userStore.users" v-loading="userStore.loading" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="fullName" label="姓名" width="120">
          <template #default="{ row }">
            {{ row.fullName || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="isSuperuser" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.isSuperuser ? 'danger' : 'primary'">
              {{ row.isSuperuser ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'info'">
              {{ row.isActive ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDialog('edit', row)">编辑</el-button>
            <el-button type="warning" link @click="showPasswordDialog(row)">改密</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="userStore.params.page"
          :page-size="userStore.params.page_size"
          :total="userStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- User Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'create'" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="管理员">
          <el-switch v-model="form.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Password Dialog -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form>
        <el-form-item label="新密码">
          <el-input v-model="newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/users'
import { usersApi } from '@/api/users'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { User } from '@/types'
import dayjs from 'dayjs'

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)

const passwordDialogVisible = ref(false)
const passwordUserId = ref<number | null>(null)
const newPassword = ref('')

const form = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  is_superuser: false
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增用户' : '编辑用户')

function showDialog(mode: 'create' | 'edit', data?: User) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    Object.assign(form, {
      username: '',
      email: '',
      full_name: '',
      password: '',
      is_superuser: false
    })
  } else {
    currentId.value = data!.id
    Object.assign(form, {
      username: data!.username,
      email: data!.email,
      full_name: data!.fullName || '',
      password: '',
      is_superuser: data!.isSuperuser
    })
  }
  dialogVisible.value = true
}

function showPasswordDialog(user: User) {
  passwordUserId.value = user.id
  newPassword.value = ''
  passwordDialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (dialogMode.value === 'create') {
          await userStore.createUser(form as any)
          ElMessage.success('创建成功')
        } else {
          await userStore.updateUser(currentId.value!, form as any)
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

async function handleChangePassword() {
  if (!newPassword.value || newPassword.value.length < 6) {
    ElMessage.error('密码长度至少6位')
    return
  }
  try {
    await usersApi.changePassword(passwordUserId.value!, '', newPassword.value)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    // Error handled by interceptor
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.deleteUser(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function search() {
  userStore.params.page = 1
  await userStore.fetchUsers()
}

async function reset() {
  userStore.params.keyword = ''
  userStore.params.page = 1
  await userStore.fetchUsers()
}

async function handlePageChange(page: number) {
  userStore.params.page = page
  await userStore.fetchUsers()
}

onMounted(() => {
  userStore.fetchUsers()
})
</script>

<style scoped>
.user-list,
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
