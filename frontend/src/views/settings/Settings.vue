<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-form ref="formRef" :model="form" label-width="140px" class="settings-form">
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-form-item label="系统名称">
          <el-input v-model="form.system_name" placeholder="请输入系统名称" />
        </el-form-item>
        
        <el-form-item label="公司名称">
          <el-input v-model="form.company_name" placeholder="请输入公司名称" />
        </el-form-item>
        
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        
        <el-form-item label="联系邮箱">
          <el-input v-model="form.contact_email" placeholder="请输入联系邮箱" />
        </el-form-item>
        
        <el-divider content-position="left">资产编号配置</el-divider>
        
        <el-form-item label="资产编号前缀">
          <el-input v-model="form.asset_code_prefix" placeholder="如 ASSET" style="width: 200px" />
          <span class="form-tip">示例: {{ assetCodeExample }}</span>
        </el-form-item>
        
        <el-divider content-position="left">数据备份</el-divider>
        
        <el-form-item label="自动备份">
          <el-switch v-model="form.auto_backup" />
        </el-form-item>
        
        <el-form-item label="备份保留天数" v-if="form.auto_backup">
          <el-input-number v-model="form.backup_retention_days" :min="1" :max="365" />
          <span class="form-tip">超过此天数的备份将自动清理</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            保存设置
          </el-button>
          <el-button @click="fetchSettings">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { settingsApi } from '@/api/settings'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  system_name: '',
  company_name: '',
  contact_email: '',
  contact_phone: '',
  asset_code_prefix: 'ASSET',
  auto_backup: true,
  backup_retention_days: 30
})

const assetCodeExample = computed(() => {
  const prefix = form.asset_code_prefix || 'ASSET'
  const year = new Date().getFullYear()
  return `${prefix}-${year}-000001`
})

async function fetchSettings() {
  try {
    const response = await settingsApi.get()
    Object.assign(form, response.data)
  } catch (error) {
    ElMessage.error('获取设置失败')
  }
}

async function handleSubmit() {
  loading.value = true
  try {
    await settingsApi.update(form)
    ElMessage.success('设置已保存')
  } catch (error) {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
}

.settings-form {
  max-width: 600px;
}

.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.el-divider {
  margin: 24px 0 16px;
}
</style>
