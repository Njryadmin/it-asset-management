<template>
  <div class="asset-detail-page page-container">
    <!-- Top Bar -->
    <div class="top-bar">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <el-button type="primary" @click="isEditing = !isEditing">
        <el-icon><Edit /></el-icon>
        {{ isEditing ? '取消编辑' : '编辑' }}
      </el-button>
    </div>

    <div v-loading="loading" class="detail-layout anim-fade-in-up">
      <!-- Left: Asset Info -->
      <div class="detail-left">
        <el-card class="info-card">
          <!-- Image placeholder -->
          <div class="asset-image-placeholder">
            <el-icon><Picture /></el-icon>
            <span>资产图片</span>
          </div>
        </el-card>

        <el-card class="info-card">
          <template #header>
            <div class="card-header-title">基本信息</div>
          </template>
          <div v-if="!isEditing" class="info-grid">
            <div class="info-item">
              <span class="info-label">资产编号</span>
              <span class="info-value">{{ asset.assetCode }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">资产名称</span>
              <span class="info-value">{{ asset.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">分类</span>
              <span class="info-value">{{ getCategoryName(asset.categoryId) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态</span>
              <el-tag :type="statusTagType(asset.status)" size="small">{{ statusLabel(asset.status) }}</el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">品牌</span>
              <span class="info-value">{{ asset.brand || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">型号</span>
              <span class="info-value">{{ asset.model || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">序列号</span>
              <span class="info-value">{{ asset.serialNumber || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">购入日期</span>
              <span class="info-value">{{ asset.purchaseDate ? dayjs(asset.purchaseDate).format('YYYY-MM-DD') : '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">保修期至</span>
              <span class="info-value">{{ asset.warrantyExpireDate ? dayjs(asset.warrantyExpireDate).format('YYYY-MM-DD') : '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">使用人</span>
              <span class="info-value">{{ asset.assignedUserName || asset.assignedTo || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">部门</span>
              <span class="info-value">{{ getDepartmentName(asset.departmentId) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">位置/地区</span>
              <span class="info-value">{{ asset.region || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">购买价格</span>
              <span class="info-value">{{ asset.purchasePrice ? `¥${asset.purchasePrice.toLocaleString()}` : '-' }}</span>
            </div>
            <div class="info-item info-item--full">
              <span class="info-label">备注</span>
              <span class="info-value">{{ asset.description || '-' }}</span>
            </div>
          </div>

          <!-- Edit Form -->
          <el-form v-else label-width="100px" class="edit-form">
            <el-form-item label="资产编号">
              <el-input v-model="form.asset_code" />
            </el-form-item>
            <el-form-item label="资产名称">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="form.category_id" style="width: 100%">
                <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="使用中" value="in_use" />
                <el-option label="闲置" value="idle" />
                <el-option label="维护中" value="maintenance" />
                <el-option label="已退役" value="retired" />
                <el-option label="已报废" value="scrapped" />
              </el-select>
            </el-form-item>
            <el-form-item label="品牌">
              <el-input v-model="form.brand" />
            </el-form-item>
            <el-form-item label="型号">
              <el-input v-model="form.model" />
            </el-form-item>
            <el-form-item label="序列号">
              <el-input v-model="form.serial_number" />
            </el-form-item>
            <el-form-item label="购入日期">
              <el-date-picker v-model="form.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="保修期至">
              <el-date-picker v-model="form.warranty_expire_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
            <el-form-item label="部门">
              <el-select v-model="form.department_id" style="width: 100%">
                <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="使用人">
              <el-input v-model="form.assigned_to" />
            </el-form-item>
            <el-form-item label="位置/地区">
              <el-input v-model="form.region" />
            </el-form-item>
            <el-form-item label="购买价格">
              <el-input-number v-model="form.purchase_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="form.description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="saveAsset">保存</el-button>
              <el-button @click="isEditing = false">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- Right: Tabs -->
      <div class="detail-right">
        <el-card class="tabs-card">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="info" />
            <el-tab-pane label="维保记录" name="maintenance">
              <el-empty description="暂无维保记录" />
            </el-tab-pane>
            <el-tab-pane label="操作日志" name="log">
              <el-table :data="auditLogs" v-loading="auditLoading" style="width: 100%" size="small">
                <el-table-column prop="createdAt" label="时间" width="160">
                  <template #default="{ row }">
                    {{ dayjs(row.createdAt).format('YYYY-MM-DD HH:mm') }}
                  </template>
                </el-table-column>
                <el-table-column prop="action" label="操作" width="100">
                  <template #default="{ row }">
                    <el-tag size="small">{{ actionLabel(row.action) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="operatorName" label="操作人" width="100" />
                <el-table-column prop="summary" label="变更摘要" show-overflow-tooltip />
              </el-table>
              <div v-if="auditLogs.length > 0" class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="auditParams.page"
                  :page-size="auditParams.page_size"
                  :total="auditTotal"
                  layout="prev, pager, next"
                  @current-change="fetchAuditLogs"
                />
              </div>
            </el-tab-pane>
            <el-tab-pane label="附件管理" name="attachments">
              <el-empty description="暂无附件" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { assetsApi } from '@/api/assets'
import { auditApi } from '@/api/auditApi'
import type { Asset } from '@/types'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const assetStore = useAssetStore()

const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const activeTab = ref('info')
const asset = ref<Asset>({} as Asset)

const auditLogs = ref<any[]>([])
const auditLoading = ref(false)
const auditTotal = ref(0)
const auditParams = reactive({ page: 1, page_size: 10 })

const form = reactive({
  asset_code: '',
  name: '',
  category_id: undefined as number | undefined,
  status: 'in_use' as string,
  brand: '',
  model: '',
  serial_number: '',
  purchase_date: '',
  warranty_expire_date: '',
  department_id: undefined as number | undefined,
  assigned_to: '',
  assignedUserName: '',
  region: '',
  purchase_price: undefined as number | undefined,
  description: ''
})

const flatCategories = computed(() => {
  const result: any[] = []
  function flatten(cats: any[], level = 0) {
    for (const cat of cats) {
      result.push({ ...cat, level })
      if (cat.children?.length) flatten(cat.children, level + 1)
    }
  }
  flatten(assetStore.categories)
  return result
})

const flatDepartments = computed(() => {
  const result: any[] = []
  function flatten(depts: any[], level = 0) {
    for (const dept of depts) {
      result.push({ ...dept, level })
      if (dept.children?.length) flatten(dept.children, level + 1)
    }
  }
  flatten(assetStore.departments)
  return result
})

function getCategoryName(id: number | null) {
  if (!id) return '-'
  const cat = flatCategories.value.find(c => c.id === id)
  return cat?.name || '-'
}

function getDepartmentName(id: number | null) {
  if (!id) return '-'
  const dept = flatDepartments.value.find(d => d.id === id)
  return dept?.name || '-'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    in_use: '使用中', idle: '闲置', maintenance: '维护中', retired: '已退役', scrapped: '已报废'
  }
  return map[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    in_use: 'success', idle: 'info', maintenance: 'warning', retired: 'danger', scrapped: 'info'
  }
  return map[status] || 'info'
}

function actionLabel(action: string) {
  const map: Record<string, string> = {
    CREATE: '创建', UPDATE: '更新', DELETE: '删除', APPROVE: '审批通过', REJECT: '审批拒绝'
  }
  return map[action] || action
}

function populateForm(a: Asset) {
  form.asset_code = a.assetCode
  form.name = a.name
  form.category_id = a.categoryId
  form.status = a.status
  form.brand = a.brand || ''
  form.model = a.model || ''
  form.serial_number = a.serialNumber || ''
  form.purchase_date = a.purchaseDate || ''
  form.warranty_expire_date = a.warrantyExpireDate || ''
  form.department_id = a.departmentId || undefined
  form.assigned_to = a.assignedTo != null ? String(a.assignedTo) : ''
  form.assignedUserName = (a as any).assignedUserName || ''
  form.region = a.region || ''
  form.purchase_price = a.purchasePrice || undefined
  form.description = a.description || ''
}

async function fetchAsset() {
  loading.value = true
  try {
    const id = Number(route.params.id)
    const res = await assetsApi.get(id)
    asset.value = res.data
    populateForm(res.data)
  } finally {
    loading.value = false
  }
}

async function fetchAuditLogs() {
  auditLoading.value = true
  try {
    const id = Number(route.params.id)
    const res = await auditApi.list({
      biz_type: 'assets',
      page: auditParams.page,
      page_size: auditParams.page_size
    })
    // Filter to only this asset's logs
    auditLogs.value = res.data.items.filter((l: any) => l.resourceId === id)
    auditTotal.value = res.data.total
  } catch {
    // ignore
  } finally {
    auditLoading.value = false
  }
}

async function saveAsset() {
  saving.value = true
  try {
    const id = Number(route.params.id)
    await assetsApi.update(id, form as any)
    ElMessage.success('保存成功')
    isEditing.value = false
    await fetchAsset()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await assetStore.fetchOptions()
  await fetchAsset()
  if (activeTab.value === 'log') {
    await fetchAuditLogs()
  }
})
</script>

<style scoped>
.asset-detail-page {
  max-width: 1400px;
  margin: 0 auto;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.detail-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 16px;
  align-items: start;
}

.detail-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  border-radius: var(--radius-lg) !important;
}

.asset-image-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: var(--wechat-bg);
  border-radius: var(--radius-md);
  color: var(--wechat-text-placeholder);
  font-size: 14px;
}

.asset-image-placeholder .el-icon {
  font-size: 48px;
  opacity: 0.5;
}

.card-header-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--wechat-text);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item--full {
  grid-column: span 2;
}

.info-label {
  font-size: 12px;
  color: var(--wechat-text-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: var(--wechat-text);
}

.edit-form {
  padding: 4px 0;
}

.detail-right .tabs-card {
  border-radius: var(--radius-lg) !important;
}

.pagination-wrapper {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
