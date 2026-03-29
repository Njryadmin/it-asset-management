<template>
  <div class="flow-config-page page-container">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">审批流程配置</h3>
            <span class="item-count">共 {{ total }} 条</span>
          </div>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建流程
          </el-button>
        </div>
      </template>

      <div v-loading="loading">
        <el-table :data="flows" stripe class="flow-table">
          <el-table-column prop="name" label="流程名称" min-width="160" />
          <el-table-column prop="flowCode" label="流程编号" min-width="160" show-overflow-tooltip />
          <el-table-column prop="applicableTo" label="适用对象" width="140">
            <template #default="{ row }">
              {{ applicableToLabel(row.applicableTo) }}
            </template>
          </el-table-column>
          <el-table-column prop="isActive" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="row.isActive ? 'success' : 'info'" size="small">
                {{ row.isActive ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="步骤数" width="90">
            <template #default="{ row }">
              {{ row.steps?.length || 0 }} 步
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          :page-size="20"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchFlows"
        />
      </div>
    </el-card>

    <!-- Create / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑流程' : '新建流程'"
      width="600px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="流程名称" prop="name">
          <el-input v-model="form.name" placeholder="如：采购申请审批流程" />
        </el-form-item>
        <el-form-item label="流程编号" prop="flowCode">
          <el-input v-model="form.flowCode" placeholder="如：PR_FLOW_001" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="适用对象" prop="applicableTo">
          <el-select v-model="form.applicableTo" placeholder="选择适用业务类型" style="width: 100%">
            <el-option label="采购申请" value="purchase_request" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态" prop="isActive">
          <el-switch v-model="form.isActive" />
        </el-form-item>

        <!-- Steps -->
        <el-form-item label="审批步骤" prop="steps">
          <div class="steps-editor">
            <div
              v-for="(step, index) in form.steps"
              :key="index"
              class="step-row"
            >
              <span class="step-num">{{ index + 1 }}</span>
              <el-input
                v-model="step.name"
                placeholder="步骤名称"
                style="flex: 1"
              />
              <el-input
                v-model="step.role"
                placeholder="审批角色"
                style="flex: 1"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="removeStep(index)"
                :disabled="form.steps.length <= 1"
              />
            </div>
            <el-button type="default" @click="addStep" style="margin-top: 8px">
              <el-icon><Plus /></el-icon>
              添加步骤
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { flowsApi, type ApprovalFlow, type ApprovalFlowForm, type ApprovalStep } from '@/api/purchases'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const loading = ref(false)
const flows = ref<ApprovalFlow[]>([])
const total = ref(0)
const page = ref(1)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref()

const form = reactive<ApprovalFlowForm>({
  name: '',
  flowCode: '',
  applicableTo: 'purchase_request',
  steps: [{ step: 1, name: '', role: '' }],
  isActive: true,
})

const rules = {
  name: [{ required: true, message: '请输入流程名称', trigger: 'blur' }],
  flowCode: [{ required: true, message: '请输入流程编号', trigger: 'blur' }],
  applicableTo: [{ required: true, message: '请选择适用对象', trigger: 'change' }],
}

function applicableToLabel(val: string) {
  const map: Record<string, string> = {
    purchase_request: '采购申请',
  }
  return map[val] || val
}

function addStep() {
  form.steps.push({ step: form.steps.length + 1, name: '', role: '' })
}

function removeStep(index: number) {
  form.steps.splice(index, 1)
  // Re-number
  form.steps.forEach((s, i) => { s.step = i + 1 })
}

async function fetchFlows() {
  loading.value = true
  try {
    const res = await flowsApi.list()
    flows.value = res.data.items || []
    total.value = res.data.total || flows.value.length
  } catch {
    ElMessage.error('加载流程列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: ApprovalFlow) {
  isEdit.value = true
  editingId.value = row.id
  form.name = row.name
  form.flowCode = row.flowCode
  form.applicableTo = row.applicableTo
  form.isActive = row.isActive
  form.steps = (row.steps && row.steps.length > 0)
    ? row.steps.map((s: any, i: number) => ({ step: i + 1, name: s.name || '', role: s.role || '' }))
    : [{ step: 1, name: '', role: '' }]
  dialogVisible.value = true
}

function resetForm() {
  form.name = ''
  form.flowCode = ''
  form.applicableTo = 'purchase_request'
  form.steps = [{ step: 1, name: '', role: '' }]
  form.isActive = true
  formRef.value?.resetFields()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  // Filter out empty steps
  const steps = form.steps.filter(s => s.name.trim() || s.role.trim())
  if (steps.length === 0) {
    ElMessage.warning('请至少填写一个有效的审批步骤')
    return
  }

  submitting.value = true
  try {
    const payload = {
      ...form,
      steps: steps.map((s, i) => ({ ...s, step: i + 1 })),
    }
    if (isEdit.value && editingId.value) {
      await flowsApi.update(editingId.value, payload)
      ElMessage.success('保存成功')
    } else {
      await flowsApi.create(payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchFlows()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: ApprovalFlow) {
  try {
    await ElMessageBox.confirm(`确定删除流程「${row.name}」？`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await flowsApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchFlows()
  } catch {
    // user cancelled
  }
}

onMounted(() => {
  fetchFlows()
})
</script>

<style scoped>
.flow-config-page {
  max-width: 1200px;
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
  color: var(--text-primary);
}

.item-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.flow-table {
  border-radius: var(--radius-md);
}

.steps-editor {
  width: 100%;
}

.step-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .flow-config-page { padding: 14px; }
}
@media (max-width: 768px) {
  .flow-config-page { padding: 10px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 10px; }
  .header-left { flex-direction: column; align-items: flex-start; gap: 4px; }
  .flow-list { }
  .flow-item { padding: 14px 12px; }
  .flow-item__meta { flex-wrap: wrap; gap: 6px; }
  .pagination-wrapper { justify-content: center; }
  .steps-editor .step-row { flex-wrap: wrap; gap: 8px; }
  .steps-editor .step-row .el-input { min-width: 0; }
}
@media (max-width: 480px) {
  .flow-config-page { padding: 8px; }
  .pagination-wrapper { justify-content: center; flex-wrap: wrap; gap: 8px; }
  .steps-editor .step-row { flex-direction: column; }
  .steps-editor .step-row .step-num { display: none; }
}

</style>
