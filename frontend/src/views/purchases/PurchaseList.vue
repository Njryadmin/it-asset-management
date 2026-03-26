<template>
  <div class="purchase-list page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">采购管理</h3>
            <span class="item-count">共 {{ purchaseStore.total }} 条</span>
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
              新增采购申请
            </el-button>
          </div>
        </div>
      </template>

      <!-- Search -->
      <div class="search-bar">
        <el-input
          v-model="purchaseStore.params.keyword"
          placeholder="搜索标题/描述..."
          clearable
          class="search-input"
          @clear="search"
          @keyup.enter="search"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="purchaseStore.params.status" placeholder="选择状态" clearable style="width: 150px" @change="search">
          <el-option label="草稿" value="draft" />
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已拒绝" value="rejected" />
          <el-option label="已采购" value="purchased" />
        </el-select>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="reset">重置</el-button>
      </div>

      <!-- Table -->
      <el-table :data="purchaseStore.requests" v-loading="purchaseStore.loading" style="width: 100%" class="data-table">
        <template v-for="col in columns" :key="col.key">
          <el-table-column v-if="col.visible && col.key === 'title'" prop="title" label="标题" min-width="150" />
          <el-table-column v-if="col.visible && col.key === 'quantity'" prop="quantity" label="数量" width="80" />
          <el-table-column v-if="col.visible && col.key === 'estimatedPrice'" prop="estimatedPrice" label="预估价格" width="110">
            <template #default="{ row }">
              {{ row.estimatedPrice ? `¥${row.estimatedPrice}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'actualPrice'" prop="actualPrice" label="实际价格" width="110">
            <template #default="{ row }">
              {{ row.actualPrice ? `¥${row.actualPrice}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'status'" prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'approverComment'" prop="approverComment" label="审批意见" width="150" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.approverComment || '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'region'" prop="region" label="地区" width="120">
            <template #default="{ row }">
              {{ row.region || '-' }}
            </template>
          </el-table-column>
          <el-table-column v-if="col.visible && col.key === 'createdAt'" prop="createdAt" label="申请时间" width="160">
            <template #default="{ row }">
              {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
            </template>
          </el-table-column>
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
                  <template v-if="row.status === 'draft'">
                    <el-dropdown-item command="submit">提交</el-dropdown-item>
                    <el-dropdown-item command="delete" style="color: #f56c6c">删除</el-dropdown-item>
                  </template>
                  <template v-else-if="row.status === 'pending' && isAdmin">
                    <el-dropdown-item command="approve">通过</el-dropdown-item>
                    <el-dropdown-item command="reject">拒绝</el-dropdown-item>
                  </template>
                  <template v-else-if="row.status === 'approved' && isAdmin">
                    <el-dropdown-item command="purchase">标记已采购</el-dropdown-item>
                  </template>
                  <el-dropdown-item v-if="row.status !== 'draft' && row.status !== 'pending' && row.status !== 'approved'" disabled>无操作</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="purchaseStore.params.page"
          :page-size="purchaseStore.params.page_size"
          :total="purchaseStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" class="custom-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="预估价格">
          <el-input-number v-model="form.estimated_price" :min="0" :precision="2" placeholder="请输入预估价格" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="form.supplier_id" placeholder="请选择供应商" clearable style="width: 100%">
            <el-option v-for="sup in purchaseStore.suppliers.filter(s => s.isActive)" :key="sup.id" :label="sup.name" :value="sup.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="form.region" placeholder="请输入地区" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Approve/Reject Dialog -->
    <el-dialog v-model="actionDialogVisible" :title="actionTitle" width="400px" class="custom-dialog">
      <el-form>
        <el-form-item label="审批意见">
          <el-input v-model="actionComment" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAction">确定</el-button>
      </template>
    </el-dialog>

    <!-- Purchase Dialog -->
    <el-dialog v-model="purchaseDialogVisible" title="标记已采购" width="400px" class="custom-dialog">
      <el-form>
        <el-form-item label="实际价格">
          <el-input-number v-model="actualPrice" :min="0" :precision="2" placeholder="请输入实际价格" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="purchaseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmPurchase">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePurchaseStore } from '@/stores/purchases'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { PurchaseRequest } from '@/types'
import { useColumnSettings } from '@/composables/useColumnSettings'
import type { ColumnOption } from '@/composables/useColumnSettings'
import dayjs from 'dayjs'

const defaultColumns: ColumnOption[] = [
  { key: 'title', label: '标题', visible: true },
  { key: 'quantity', label: '数量', visible: true },
  { key: 'estimatedPrice', label: '预估价格', visible: true },
  { key: 'actualPrice', label: '实际价格', visible: false },
  { key: 'status', label: '状态', visible: true },
  { key: 'approverComment', label: '审批意见', visible: false },
  { key: 'region', label: '地区', visible: true },
  { key: 'createdAt', label: '申请时间', visible: true }
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
} = useColumnSettings('purchase-columns', defaultColumns)

const purchaseStore = usePurchaseStore()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)

const actionDialogVisible = ref(false)
const actionTitle = ref('')
const actionType = ref<'approve' | 'reject'>('approve')
const actionComment = ref('')
const actionRequestId = ref<number | null>(null)

const purchaseDialogVisible = ref(false)
const actualPrice = ref<number | undefined>()
const purchaseRequestId = ref<number | null>(null)

const isAdmin = computed(() => authStore.user?.isSuperuser)

const form = reactive({
  title: '',
  description: '',
  quantity: 1,
  estimated_price: undefined as number | undefined,
  supplier_id: undefined as number | undefined,
  region: ''
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增采购申请' : '编辑采购申请')

const statusMap: Record<string, string> = {
  draft: '草稿',
  pending: '待审批',
  approved: '已通过',
  rejected: '已拒绝',
  purchased: '已采购'
}

function statusLabel(status: string) {
  return statusMap[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, any> = {
    draft: 'info',
    pending: 'warning',
    approved: 'success',
    rejected: 'danger',
    purchased: 'success'
  }
  return map[status] || 'info'
}

function handleActionCommand(cmd: string, row: PurchaseRequest) {
  if (cmd === 'submit') handleSubmitRequest(row.id)
  else if (cmd === 'delete') handleDelete(row.id)
  else if (cmd === 'approve') handleApprove(row)
  else if (cmd === 'reject') handleReject(row)
  else if (cmd === 'purchase') handlePurchase(row)
}

function showDialog(mode: 'create' | 'edit', data?: PurchaseRequest) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    Object.assign(form, {
      title: '',
      description: '',
      quantity: 1,
      estimated_price: undefined,
      supplier_id: undefined,
      region: ''
    })
  } else {
    currentId.value = data!.id
    Object.assign(form, {
      title: data!.title,
      description: data!.description || '',
      quantity: data!.quantity,
      estimated_price: data!.estimatedPrice,
      supplier_id: data!.supplierId ?? undefined,
      region: data!.region || ''
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
          await purchaseStore.create(form as any)
          ElMessage.success('创建成功')
        } else {
          await purchaseStore.update(currentId.value!, form as any)
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

async function handleSubmitRequest(id: number) {
  try {
    await ElMessageBox.confirm('确定要提交此采购申请吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await purchaseStore.submit(id)
    ElMessage.success('提交成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  }
}

function handleApprove(row: PurchaseRequest) {
  actionType.value = 'approve'
  actionTitle.value = '审批通过'
  actionRequestId.value = row.id
  actionComment.value = ''
  actionDialogVisible.value = true
}

function handleReject(row: PurchaseRequest) {
  actionType.value = 'reject'
  actionTitle.value = '审批拒绝'
  actionRequestId.value = row.id
  actionComment.value = ''
  actionDialogVisible.value = true
}

async function confirmAction() {
  try {
    if (actionType.value === 'approve') {
      await purchaseStore.approve(actionRequestId.value!, actionComment.value)
      ElMessage.success('审批通过')
    } else {
      await purchaseStore.reject(actionRequestId.value!, actionComment.value)
      ElMessage.success('已拒绝')
    }
    actionDialogVisible.value = false
  } catch (error) {
    // Error handled by interceptor
  }
}

function handlePurchase(row: PurchaseRequest) {
  purchaseRequestId.value = row.id ?? null
  actualPrice.value = row.estimatedPrice ?? undefined
  purchaseDialogVisible.value = true
}

async function confirmPurchase() {
  try {
    await purchaseStore.markPurchased(purchaseRequestId.value!, actualPrice.value)
    ElMessage.success('已标记为已采购')
    purchaseDialogVisible.value = false
  } catch (error) {
    // Error handled by interceptor
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除此采购申请吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await purchaseStore.remove(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function search() {
  purchaseStore.params.page = 1
  await purchaseStore.fetchRequests()
}

async function reset() {
  purchaseStore.params.keyword = ''
  purchaseStore.params.status = ''
  purchaseStore.params.page = 1
  await purchaseStore.fetchRequests()
}

async function handlePageChange(page: number) {
  purchaseStore.params.page = page
  await purchaseStore.fetchRequests()
}

onMounted(() => {
  purchaseStore.fetchRequests()
  purchaseStore.fetchSuppliers()
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

.no-action {
  color: var(--wechat-text-placeholder);
  font-size: 12px;
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
</style>
