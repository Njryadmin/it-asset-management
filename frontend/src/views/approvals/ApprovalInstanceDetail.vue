<template>
  <div class="approval-detail-page page-container">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon> 加载中...
    </div>

    <template v-else-if="instance">
      <!-- Top Info Card -->
      <el-card class="info-card">
        <template #header>
          <span class="card-title">审批详情</span>
          <el-tag :type="statusTagType(instance.status)" size="small">{{ statusLabel(instance.status) }}</el-tag>
        </template>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">申请单号</span>
            <span class="info-value">{{ instance.instanceNo || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">申请人</span>
            <span class="info-value">{{ instance.applicantName || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">申请时间</span>
            <span class="info-value">{{ dayjs(instance.createdAt).format('YYYY-MM-DD HH:mm') }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">业务类型</span>
            <span class="info-value">{{ instance.bizType === 'purchase_request' ? '采购申请' : instance.bizType }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">当前步骤</span>
            <span class="info-value">{{ instance.currentStep }} / {{ instance.totalSteps || '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- Purchase Request Summary -->
      <el-card v-if="instance.bizType === 'purchase_request'" class="info-card" style="margin-top: 16px;">
        <template #header>
          <span class="card-title">采购申请摘要</span>
        </template>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">采购标题</span>
            <span class="info-value">{{ instance.bizTitle || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">预估金额</span>
            <span class="info-value amount">{{ instance.bizPrice ? '¥' + instance.bizPrice.toLocaleString() : '-' }}</span>
          </div>
        </div>
      </el-card>

      <!-- Approval Progress -->
      <el-card class="info-card" style="margin-top: 16px;">
        <template #header>
          <span class="card-title">审批进度</span>
        </template>
        <el-steps :active="activeStepIndex" finish-status="success" align-center>
          <el-step
            v-for="n in (instance.totalSteps || 1)"
            :key="n"
            :title="`步骤 ${n}`"
            :status="stepStatus(n)"
          />
        </el-steps>
      </el-card>

      <!-- Approval Chain Records -->
      <el-card class="info-card" style="margin-top: 16px;">
        <template #header>
          <span class="card-title">审批记录</span>
        </template>
        <el-timeline v-if="instance.approvalChain && instance.approvalChain.length > 0">
          <el-timeline-item
            v-for="(record, idx) in instance.approvalChain"
            :key="idx"
            :type="record.action === 'approve' ? 'success' : 'danger'"
            :timestamp="record.time ? dayjs(record.time).format('YYYY-MM-DD HH:mm') : ''"
            :hollow="record.action !== 'approve' && record.action !== 'reject'"
          >
            <div class="chain-item">
              <div class="chain-header">
                <span class="chain-approver">{{ record.approver || '未知' }}</span>
                <el-tag :type="record.action === 'approve' ? 'success' : 'danger'" size="small">
                  {{ record.action === 'approve' ? '通过' : record.action === 'reject' ? '拒绝' : record.action }}
                </el-tag>
              </div>
              <div v-if="record.comment" class="chain-comment">
                {{ record.comment }}
              </div>
              <div class="chain-step">步骤 {{ record.step }}</div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无审批记录" />
      </el-card>

      <!-- Action Buttons (pending + approver) -->
      <div v-if="instance.status === 'pending' && isCurrentApprover" class="action-bar">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="openApproveDialog">通过</el-button>
        <el-button type="danger" @click="openRejectDialog">拒绝</el-button>
      </div>
      <div v-else-if="instance.status !== 'pending'" class="action-bar">
        <el-button @click="goBack">返回</el-button>
      </div>
    </template>

    <!-- Not found -->
    <el-empty v-else description="审批实例不存在" />

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
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { approvalApi, type ApprovalInstance, type ApprovalChainItem } from '@/api/purchases'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const instance = ref<ApprovalInstance | null>(null)
const loading = ref(false)
const submitting = ref(false)
const showApproveDialog = ref(false)
const showRejectDialog = ref(false)
const approvalForm = reactive({ comment: '' })

const isCurrentApprover = computed(() => {
  // Approver check: in a real app, compare with flow step approvers
  // For now, allow any superuser or the applicant themselves
  const user = authStore.user
  return user && (user.isSuperuser || user.id === instance.value?.applicantId)
})

const activeStepIndex = computed(() => {
  if (!instance.value) return 0
  // Steps 1..N, active step is currentStep - 1 (completed steps shown as success)
  return Math.min(instance.value.currentStep - 1, instance.value.totalSteps || 1)
})

function stepStatus(step: number): string {
  if (!instance.value) return 'wait'
  const chain = instance.value.approvalChain || []
  // Find if this step has been acted on
  const stepRecord = chain.find(r => r.step === step)
  if (stepRecord) {
    return stepRecord.action === 'approve' ? 'success' : 'error'
  }
  if (step < instance.value.currentStep) return 'success'
  if (step === instance.value.currentStep) return 'process'
  return 'wait'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待审批', approved: '已通过', rejected: '已拒绝'
  }
  return map[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'warning', approved: 'success', rejected: 'danger'
  }
  return map[status] || 'info'
}

async function fetchDetail() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const res: any = await approvalApi.get(id)
    instance.value = res.data
  } catch {
    ElMessage.error('加载审批详情失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

function openApproveDialog() {
  approvalForm.comment = ''
  showApproveDialog.value = true
}

function openRejectDialog() {
  approvalForm.comment = ''
  showRejectDialog.value = true
}

async function submitApprove() {
  if (!instance.value) return
  submitting.value = true
  try {
    await approvalApi.approve(instance.value.id, { comment: approvalForm.comment })
    ElMessage.success('审批已通过')
    showApproveDialog.value = false
    await fetchDetail()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

async function submitReject() {
  if (!instance.value) return
  if (!approvalForm.comment.trim()) {
    ElMessage.warning('请填写拒绝原因')
    return
  }
  submitting.value = true
  try {
    await approvalApi.reject(instance.value.id, { comment: approvalForm.comment })
    ElMessage.success('已拒绝该申请')
    showRejectDialog.value = false
    await fetchDetail()
  } catch {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.approval-detail-page {
  max-width: 900px;
  margin: 0 auto;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--wechat-text-secondary);
  padding: 60px;
}

.info-card {
  border-radius: var(--radius-lg) !important;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--wechat-text);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--wechat-text-secondary);
}

.info-value {
  font-size: 14px;
  color: var(--wechat-text);
  font-weight: 500;
}

.info-value.amount {
  color: var(--wechat-warning);
  font-weight: 600;
}

.chain-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chain-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chain-approver {
  font-weight: 600;
  font-size: 14px;
  color: var(--wechat-text);
}

.chain-comment {
  font-size: 13px;
  color: var(--wechat-text-secondary);
  padding: 4px 0;
}

.chain-step {
  font-size: 12px;
  color: var(--wechat-text-secondary);
}

.action-bar {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 0;
}
</style>
