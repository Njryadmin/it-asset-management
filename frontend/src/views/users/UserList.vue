<template>
  <div class="user-list page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">用户管理</h3>
            <span class="item-count">共 {{ userStore.total }} 条</span>
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
            <el-button type="primary" @click="showDialog('create')">
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
          </div>
        </div>
      </template>

      <!-- Search -->
      <div class="search-bar">
        <el-input
          v-model="userStore.params.keyword"
          placeholder="搜索用户名/邮箱/姓名..."
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

      <!-- Table -->
      <el-table :data="userStore.users" v-loading="userStore.loading" style="width: 100%" class="data-table">
        <template v-for="col in columns" :key="col.key">
          <el-table-column v-if="col.visible && col.key === 'username'" prop="username" label="用户名" width="120" />
          <el-table-column v-if="col.visible && col.key === 'email'" prop="email" label="邮箱" width="180" />
          <el-table-column v-if="col.visible && col.key === 'fullName'" prop="fullName" label="姓名" width="120">
            <template #default="{ row }">
              {{ row.fullName || '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'isSuperuser'" prop="isSuperuser" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.isSuperuser ? 'danger' : 'primary'">
                {{ row.isSuperuser ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'isActive'" prop="isActive" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isActive ? 'success' : 'info'">
                {{ row.isActive ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'createdAt'" prop="createdAt" label="创建时间" width="160">
            <template #default="{ row }">
              {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
            </template>
          </el-table-column>
        </template>
        <el-table-column label="操作" min-width="200" fixed="right">
          <template #default="{ row }">
            <div class="action-btn-group">
              <span class="action-link" @click="showDialog('edit', row)">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </span>
              <span class="action-link" :class="row.isActive ? 'action-link--warning' : 'action-link--success'" @click="handleToggleStatus(row)">
                <el-icon><Switch /></el-icon>
                <span>{{ row.isActive ? '禁用' : '启用' }}</span>
              </span>
              <span class="action-link action-link--warning" @click="handleResetPassword(row)">
                <el-icon><Key /></el-icon>
                <span>重置密码</span>
              </span>
              <span class="action-link action-link--danger" @click="handleDelete(row.id)">
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </span>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="90%" max-width="500px" class="custom-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input id="user-username" name="username" v-model="form.username" placeholder="请输入用户名" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input id="user-email" name="email" v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input id="user-fullname" name="full_name" v-model="form.full_name" placeholder="请输入姓名" />
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
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="90%" max-width="400px" class="custom-dialog">
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

    <!-- Password Reset Dialog -->
    <el-dialog v-model="resetPasswordDialogVisible" title="重置密码" width="90%" max-width="420px" class="custom-dialog">
      <div v-if="tempPassword" class="reset-password-result">
        <p class="reset-password-tip">临时密码（请复制保存）：</p>
        <el-input v-model="tempPassword" readonly click-to-select class="temp-password-input">
          <template #append>
            <el-button @click="copyTempPassword" :icon="CopyDocument">复制</el-button>
          </template>
        </el-input>
        <p class="reset-password-note">⚠️ 用户首次登录后必须修改密码</p>
      </div>
      <div v-else class="reset-password-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在重置密码...</span>
      </div>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">关闭</el-button>
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
import { useColumnSettings } from '@/composables/useColumnSettings'
import type { ColumnOption } from '@/composables/useColumnSettings'
import { CopyDocument, Loading } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const defaultColumns: ColumnOption[] = [
  { key: 'username', label: '用户名', visible: true },
  { key: 'email', label: '邮箱', visible: true },
  { key: 'fullName', label: '姓名', visible: true },
  { key: 'isSuperuser', label: '角色', visible: true },
  { key: 'isActive', label: '状态', visible: true },
  { key: 'createdAt', label: '创建时间', visible: true }
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
} = useColumnSettings('user-columns', defaultColumns)

const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)
const passwordDialogVisible = ref(false)
const passwordUserId = ref<number | null>(null)
const resetPasswordDialogVisible = ref(false)
const tempPassword = ref('')
const resetPasswordUsername = ref('')
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

function handleActionCommand(cmd: string, row: User) {
  if (cmd === 'password') showPasswordDialog(row)
  else if (cmd === 'delete') handleDelete(row.id)
}

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
    // Admin can change password without old password
    await usersApi.changePassword(passwordUserId.value!, undefined, newPassword.value)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    // Error handled by interceptor
  }
}

async function handleResetPassword(row: User) {
  try {
    const confirmed = await ElMessageBox.confirm(
      `确定要重置用户「${row.username}」的密码吗？重置后将生成新的临时密码。`,
      '重置密码',
      { confirmButtonText: '确定重置', cancelButtonText: '取消', type: 'warning' }
    )
    resetPasswordUsername.value = row.username
    tempPassword.value = ''
    resetPasswordDialogVisible.value = true
    const res = await usersApi.resetPassword(row.id)
    tempPassword.value = res.data.temp_password
  } catch (error) {
    // User cancelled or error
  }
}

async function copyTempPassword() {
  try {
    await navigator.clipboard.writeText(tempPassword.value)
    ElMessage.success('临时密码已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动选择文本复制')
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

async function handleToggleStatus(row: User) {
  const action = row.isActive ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await usersApi.toggleStatus(row.id)
    ElMessage.success(`${action}成功`)
    await userStore.fetchUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
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
  color: var(--text-primary);
}

.item-count {
  font-size: 13px;
  color: var(--text-secondary);
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

/* ── Tablet ── */
@media (max-width: 1024px) {
  .user-page { padding: 14px; }
}
/* ── Small Mobile ── */
@media (max-width: 480px) {
  .user-page { padding: 8px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .search-bar { flex-wrap: wrap; gap: 8px; }
  .search-input { width: 100%; min-width: 0; }
  .pagination { justify-content: center; flex-wrap: wrap; gap: 8px; }
}

.reset-password-result { display: flex; flex-direction: column; gap: 12px; }
.reset-password-tip { font-size: 14px; color: var(--text-primary); margin: 0; }
.temp-password-input { font-family: 'SF Mono','Monaco',monospace; font-size: 18px; }
.reset-password-note { font-size: 12px; color: var(--text-secondary); margin: 0; }
.reset-password-loading { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 20px 0; color: var(--text-secondary); }

</style>
