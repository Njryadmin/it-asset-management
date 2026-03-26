<template>
  <div class="purchase-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购管理</span>
          <el-button type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            新增采购申请
          </el-button>
        </div>
      </template>

      <!-- Search -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="purchaseStore.params.keyword" placeholder="搜索标题/描述" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="purchaseStore.params.status" placeholder="选择状态" clearable @change="search">
            <el-option label="草稿" value="draft" />
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已采购" value="purchased" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table :data="purchaseStore.requests" v-loading="purchaseStore.loading" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="estimatedPrice" label="预估价格" width="110">
          <template #default="{ row }">
            {{ row.estimatedPrice ? `¥${row.estimatedPrice}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actualPrice" label="实际价格" width="110">
          <template #default="{ row }">
            {{ row.actualPrice ? `¥${row.actualPrice}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="申请时间" width="160">
          <template #default="{ row }">
            {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" type="primary" link @click="handleSubmitRequest(row.id)">提交</el-button>
            <el-button v-if="row.status === 'pending'" type="success" link @click="handleApprove(row)">通过</el-button>
            <el-button v-if="row.status === 'pending'" type="danger" link @click="handleReject(row)">拒绝</el-button>
            <el-button v-if="row.status === 'approved'" type="warning" link @click="handlePurchase(row)">标记已采购</el-button>
            <el-button type="primary" link @click="showDialog('edit', row)">编辑</el-button>
            <el-button v-if="row.status === 'draft'" type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Approve/Reject Dialog -->
    <el-dialog v-model="actionDialogVisible" :title="actionTitle" width="400px">
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
    <el-dialog v-model="purchaseDialogVisible" title="标记已采购" width="400px">
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
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { PurchaseRequest, PurchaseRequestForm } from '@/types'
import dayjs from 'dayjs'

const purchaseStore = usePurchaseStore()
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

const form = reactive<PurchaseRequestForm>({
  title: '',
  description: '',
  quantity: 1,
  estimated_price: undefined
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

function showDialog(mode: 'create' | 'edit', data?: PurchaseRequest) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    Object.assign(form, {
      title: '',
      description: '',
      quantity: 1,
      estimated_price: undefined
    })
  } else {
    currentId.value = data!.id
    Object.assign(form, {
      title: data!.title,
      description: data!.description || '',
      quantity: data!.quantity,
      estimated_price: data!.estimatedPrice
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
          await purchaseStore.create(form)
          ElMessage.success('创建成功')
        } else {
          await purchaseStore.update(currentId.value!, form)
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
