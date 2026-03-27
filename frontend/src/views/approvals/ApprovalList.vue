<template>
  <div class="approval-page page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">审批管理</h3>
            <span class="item-count">共 {{ total }} 条</span>
          </div>
        </div>
      </template>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <el-tab-pane label="我的申请" name="my" />
        <el-tab-pane v-if="authStore.user?.isSuperuser" label="待我审批" name="pending" />
        <el-tab-pane label="审批历史" name="history" />
      </el-tabs>

      <!-- Filter for pending tab -->
      <div v-if="activeTab === 'pending'" class="filter-bar">
        <el-input v-model="filterParams.keyword" placeholder="搜索申请人/事由" clearable style="width: 200px" @change="fetchApprovals" />
        <el-button @click="resetFilters">重置</el-button>
        <el-button type="primary" @click="fetchApprovals">查询</el-button>
      </div>

      <!-- Loading -->
      <div v-loading="loading" class="card-list anim-fade-in-up">
        <!-- Empty state -->
        <el-empty v-if="!loading && approvals.length === 0" :description="emptyDescription" />

        <!-- Approval cards -->
        <div v-else class="approval-grid">
          <el-card
            v-for="item in approvals"
            :key="item.id"
            class="approval-card"
            shadow="hover"
          >
            <div class="approval-card__header">
              <div class="approval-card__title">{{ item.instanceNo || '申请 ' + item.id }}</div>
              <el-tag :type="statusTagType(item.status)" size="small">{{ statusLabel(item.status) }}</el-tag>
            </div>
            <div class="approval-card__body">
              <div class="approval-card__row">
                <span class="label">申请人</span>
                <span class="value">{{ item.applicantName || '-' }}</span>
              </div>
              <div class="approval-card__row">
                <span class="label">申请时间</span>
                <span class="value">{{ dayjs(item.createdAt).format('YYYY-MM-DD HH:mm') }}</span>
              </div>
              <div class="approval-card__row">
                <span class="label">申请类型</span>
                <span class="value">{{ item.bizType === 'purchase_request' ? '采购申请' : item.bizType }}</span>
              </div>
            </div>
            <div v-if="activeTab === 'pending' && item.status === 'pending'" class="approval-card__footer">
              <el-button size="small" type="primary" @click="openApproveDialog(item)">通过</el-button>
              <el-button size="small" type="danger" @click="openRejectDialog(item)">拒绝</el-button>
            </div>
          </el-card>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="filterParams.page"
          :page-size="filterParams.page_size"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchApprovals"
        />
      </div>
    </el-card>

    <!-- Approve Dialog -->
    <el-dialog v-model="showApproveDialog" title="审批通过" width="420px">
      <el-form label-width="80px">
        <el-form-item label="审批意见">
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="填写审批意见（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApproveDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitApprove">确认通过</el-button>
      </template>
    </el-dialog>

    <!-- Reject Dialog -->
    <el-dialog v-model="showRejectDialog" title="审批拒绝" width="420px">
      <el-form label-width="80px">
        <el-form-item label="拒绝原因" required>
          <el-input v-model="approvalForm.comment" type="textarea" :rows="3" placeholder="请填写拒绝原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="submitReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { approvalApi, type ApprovalInstance } from '@/api/purchases'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const authStore = useAuthStore()
const activeTab = ref('my')
const loading = ref(false)
const approvals = ref<ApprovalInstance[]>([])
const total = ref(0)
const showApproveDialog = ref(false)
const showRejectDialog = ref(false)
const submitting = ref(false)
const currentItem = ref<ApprovalInstance | null>(null)

const filterParams = reactive({
  keyword: '',
  page: 1,
  page_size: 20
})

const emptyDescription = computed(() => {
  if (activeTab.value === 'my') return '暂无我的申请'
  if (activeTab.value === 'pending') return '暂无待审批任务'
  return '暂无审批历史'
})

function onTabChange() {
  filterParams.page = 1
  filterParams.keyword = ''
  fetchApprovals()
}

async function fetchApprovals() {
  loading.value = true
  try {
    let res: any
    if (activeTab.value === 'my') {
      res = await approvalApi.myApplications({ page: filterParams.page, page_size: filterParams.page_size })
      approvals.value = res.data.items
      total.value = res.data.total
    } else if (activeTab.value === 'pending') {
      res = await approvalApi.myPending({ page: filterParams.page, page_size: filterParams.page_size })
      approvals.value = res.data.items || []
      total.value = res.data.total || 0
    } else {
      res = await approvalApi.myHistory({ page: filterParams.page, page_size: filterParams.page_size })
      approvals.value = res.data.items
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filterParams.keyword = ''
  fetchApprovals()
}

function openApproveDialog(item: ApprovalInstance) {
  currentItem.value = item
  approvalForm.comment = ''
  showApproveDialog.value = true
}

function openRejectDialog(item: ApprovalInstance) {
  currentItem.value = item
  approvalForm.comment = ''
  showRejectDialog.value = true
}

const approvalForm = reactive({ comment: '' })

async function submitApprove() {
  if (!currentItem.value) return
  submitting.value = true
  try {
    await approvalApi.approve(currentItem.value.id, { comment: approvalForm.comment })
    ElMessage.success('审批已通过')
    showApproveDialog.value = false
    fetchApprovals()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

async function submitReject() {
  if (!currentItem.value) return
  if (!approvalForm.comment.trim()) {
    ElMessage.warning('请填写拒绝原因')
    return
  }
  submitting.value = true
  try {
    await approvalApi.reject(currentItem.value.id, { comment: approvalForm.comment })
    ElMessage.success('已拒绝该申请')
    showRejectDialog.value = false
    fetchApprovals()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return map[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return map[status] || 'info'
}

onMounted(() => {
  fetchApprovals()
})
</script>

<style scoped>
.approval-page {
  max-width: 1400px;
  margin: 0 auto;
}

.main-card {
  border-radius: var(--radius-lg) !important;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.card-list {
  min-height: 200px;
}

.approval-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.approval-card {
  border-radius: var(--radius-md) !important;
  transition: box-shadow var(--transition-normal);
}

.approval-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 12px;
}

.approval-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--wechat-text);
  flex: 1;
  line-height: 1.4;
}

.approval-card__body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.approval-card__row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.approval-card__row .label {
  font-size: 13px;
  color: var(--wechat-text-secondary);
  min-width: 68px;
  flex-shrink: 0;
}

.approval-card__row .value {
  font-size: 13px;
  color: var(--wechat-text);
  flex: 1;
}

.approval-card__row .amount {
  font-weight: 600;
  color: var(--wechat-warning);
}

.approval-card__row .comment {
  color: var(--wechat-text-secondary);
  font-style: italic;
}

.approval-card__footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--wechat-border-light);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
