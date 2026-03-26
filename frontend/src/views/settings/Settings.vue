<template>
  <div class="settings">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- 基础设置 -->
        <el-tab-pane label="基础设置" name="basic">
          <el-form ref="basicFormRef" :model="basicForm" label-width="140px" class="settings-form">
            <el-divider content-position="left">基本信息</el-divider>
            
            <el-form-item label="系统名称">
              <el-input v-model="basicForm.system_name" placeholder="请输入系统名称" />
            </el-form-item>
            
            <el-form-item label="公司名称">
              <el-input v-model="basicForm.company_name" placeholder="请输入公司名称" />
            </el-form-item>
            
            <el-form-item label="联系电话">
              <el-input v-model="basicForm.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
            
            <el-form-item label="联系邮箱">
              <el-input v-model="basicForm.contact_email" placeholder="请输入联系邮箱" />
            </el-form-item>
            
            <el-divider content-position="left">资产编号配置</el-divider>
            
            <el-form-item label="资产编号前缀">
              <el-input v-model="basicForm.asset_code_prefix" placeholder="如 ASSET" style="width: 200px" />
              <span class="form-tip">示例: {{ assetCodeExample }}</span>
            </el-form-item>
            
            <el-divider content-position="left">数据备份</el-divider>
            
            <el-form-item label="自动备份">
              <el-switch v-model="basicForm.auto_backup" />
            </el-form-item>
            
            <el-form-item label="备份保留天数" v-if="basicForm.auto_backup">
              <el-input-number v-model="basicForm.backup_retention_days" :min="1" :max="365" />
              <span class="form-tip">超过此天数的备份将自动清理</span>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="basicLoading" @click="saveBasicSettings">
                保存设置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 主题设置 -->
        <el-tab-pane label="主题设置" name="theme">
          <div class="theme-section">
            <el-divider content-position="left">选择主题</el-divider>
            <div class="theme-list">
              <div 
                v-for="(theme, key) in themes" 
                :key="String(key)"
                class="theme-card"
                :class="{ active: currentTheme === String(key) }"
                @click="selectTheme(String(key))"
              >
                <div class="theme-preview" :style="getThemePreviewStyle(theme)">
                  <div class="preview-sidebar" :style="{ background: theme.sidebar_color }"></div>
                  <div class="preview-content">
                    <div class="preview-header" :style="{ background: theme.header_color }"></div>
                    <div class="preview-body"></div>
                  </div>
                </div>
                <div class="theme-name">{{ theme.name }}</div>
                <el-icon v-if="currentTheme === String(key)" class="theme-check"><Check /></el-icon>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 个人设置 -->
        <el-tab-pane label="个人设置" name="profile">
          <el-form ref="profileFormRef" :model="profileForm" label-width="140px" class="settings-form">
            <el-divider content-position="left">个人信息</el-divider>
            
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            
            <el-form-item label="邮箱">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            
            <el-form-item label="姓名">
              <el-input v-model="profileForm.full_name" placeholder="请输入姓名" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="profileLoading" @click="saveProfile">
                保存个人信息
              </el-button>
              <el-button @click="resetProfile">重置</el-button>
            </el-form-item>
            
            <el-divider content-position="left">修改密码</el-divider>
            
            <el-form-item label="原密码">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入原密码" show-password />
            </el-form-item>
            
            <el-form-item label="新密码">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" show-password />
            </el-form-item>
            
            <el-form-item label="确认新密码">
              <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" :loading="passwordLoading" @click="changePassword">
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const activeTab = ref('basic')
const basicLoading = ref(false)
const profileLoading = ref(false)
const passwordLoading = ref(false)
const basicFormRef = ref<FormInstance>()
const profileFormRef = ref<FormInstance>()

// Local theme definitions (must match App.vue)
const localThemes = {
  default: {
    name: '默认主题',
    primary: '#409eff',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',
    bg_color: '#f0f2f5',
    sidebar_color: '#304156',
    sidebar_text: '#bfcbd9',
    sidebar_active: '#263445',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#303133',
    text_secondary: '#606266',
    border_color: '#e4e7ed',
    border_light: '#f0f2f5',
    shadow: '0 2px 12px rgba(0,0,0,0.08)',
    shadow_hover: '0 4px 20px rgba(0,0,0,0.12)'
  },
  dark: {
    name: '深色主题',
    primary: '#409eff',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',
    bg_color: '#0d1117',
    sidebar_color: '#161b22',
    sidebar_text: '#8b949e',
    sidebar_active: 'rgba(31,111,235,0.2)',
    header_color: '#161b22',
    card_bg: '#161b22',
    text_primary: '#c9d1d9',
    text_secondary: '#8b949e',
    border_color: '#30363d',
    border_light: '#21262d',
    shadow: '0 2px 12px rgba(0,0,0,0.4)',
    shadow_hover: '0 4px 20px rgba(0,0,0,0.5)'
  },
  green: {
    name: '绿色主题',
    primary: '#2eb872',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',
    bg_color: '#f0f9eb',
    sidebar_color: '#1a5c1a',
    sidebar_text: '#a6e7b0',
    sidebar_active: 'rgba(46,184,114,0.13)',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#303133',
    text_secondary: '#606266',
    border_color: '#e1f3d8',
    border_light: '#f0f9eb',
    shadow: '0 2px 12px rgba(46,184,114,0.12)',
    shadow_hover: '0 4px 20px rgba(46,184,114,0.2)'
  },
  purple: {
    name: '紫色主题',
    primary: '#a371f7',
    success: '#67c23a',
    warning: '#e6a23c',
    danger: '#f56c6c',
    info: '#909399',
    bg_color: '#f5f3ff',
    sidebar_color: '#2d1b4e',
    sidebar_text: '#d2b4fa',
    sidebar_active: 'rgba(163,113,247,0.13)',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#303133',
    text_secondary: '#606266',
    border_color: '#ede9fe',
    border_light: '#f5f3ff',
    shadow: '0 2px 12px rgba(163,113,247,0.12)',
    shadow_hover: '0 4px 20px rgba(163,113,247,0.2)'
  }
}

const themes: any = ref(localThemes)
const currentTheme = ref(localStorage.getItem('app-theme') || 'default')

const basicForm = reactive({
  system_name: '',
  company_name: '',
  contact_email: '',
  contact_phone: '',
  asset_code_prefix: 'ASSET',
  auto_backup: true,
  backup_retention_days: 30
})

const profileForm = reactive({
  username: '',
  email: '',
  full_name: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const assetCodeExample = computed(() => {
  const prefix = basicForm.asset_code_prefix || 'ASSET'
  const year = new Date().getFullYear()
  return `${prefix}-${year}-000001`
})

function getThemePreviewStyle(theme: any) {
  return {
    '--theme-bg': theme.bg_color,
    '--theme-sidebar': theme.sidebar_color,
    '--theme-header': theme.header_color
  }
}

async function fetchSettings() {
  try {
    const response = await settingsApi.get()
    Object.assign(basicForm, response.data)
  } catch (error) {
    ElMessage.error('获取设置失败')
  }
}

async function fetchThemes() {
  try {
    const response = await settingsApi.getThemes()
    themes.value = response.data
  } catch (error) {
    console.error('Failed to fetch themes:', error)
  }
}

async function fetchProfile() {
  try {
    const response = await settingsApi.getProfile()
    Object.assign(profileForm, response.data)
  } catch (error) {
    console.error('Failed to fetch profile:', error)
  }
}

async function saveBasicSettings() {
  basicLoading.value = true
  try {
    await settingsApi.update(basicForm)
    ElMessage.success('设置已保存')
  } catch (error) {
    // Error handled by interceptor
  } finally {
    basicLoading.value = false
  }
}

function selectTheme(key: string) {
  currentTheme.value = key
  const theme = themes.value[key]
  if (theme) {
    const root = document.documentElement
    // Apply all CSS variables matching App.vue
    root.style.setProperty('--el-color-primary', theme.primary)
    root.style.setProperty('--theme-bg', theme.bg_color)
    root.style.setProperty('--theme-sidebar', theme.sidebar_color)
    root.style.setProperty('--theme-sidebar-text', theme.sidebar_text)
    root.style.setProperty('--theme-sidebar-active', theme.sidebar_active)
    root.style.setProperty('--theme-header', theme.header_color)
    root.style.setProperty('--theme-card', theme.card_bg)
    root.style.setProperty('--theme-text-primary', theme.text_primary)
    root.style.setProperty('--theme-text-secondary', theme.text_secondary)
    root.style.setProperty('--theme-border', theme.border_color)
    root.style.setProperty('--theme-border-light', theme.border_light)
    root.style.setProperty('--theme-shadow', theme.shadow)
    root.style.setProperty('--theme-shadow-hover', theme.shadow_hover)
    // Aliases for global.css compatibility
    root.style.setProperty('--theme-primary', theme.primary)
    root.style.setProperty('--theme-success', theme.success)
    root.style.setProperty('--theme-warning', theme.warning)
    root.style.setProperty('--theme-danger', theme.danger)
    root.style.setProperty('--theme-info', theme.info)
    root.setAttribute('data-theme', key)
    localStorage.setItem('app-theme', key)
  }
  ElMessage.success(`已切换到${theme.name}`)
}

function saveProfile() {
  profileLoading.value = true
  settingsApi.updateProfile(profileForm).then(() => {
    ElMessage.success('个人信息已保存')
  }).catch(() => {
    // Error handled by interceptor
  }).finally(() => {
    profileLoading.value = false
  })
}

function resetProfile() {
  fetchProfile()
}

function changePassword() {
  if (!passwordForm.old_password) {
    ElMessage.error('请输入原密码')
    return
  }
  if (!passwordForm.new_password) {
    ElMessage.error('请输入新密码')
    return
  }
  if (passwordForm.new_password.length < 6) {
    ElMessage.error('新密码长度至少6位')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }
  
  passwordLoading.value = true
  settingsApi.changePassword(passwordForm.old_password, passwordForm.new_password)
    .then(() => {
      ElMessage.success('密码修改成功')
      resetPasswordForm()
    })
    .catch(() => {
      // Error handled by interceptor
    })
    .finally(() => {
      passwordLoading.value = false
    })
}

function resetPasswordForm() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

onMounted(() => {
  fetchSettings()
  // themes are loaded from local definitions
  fetchProfile()
})
</script>

<style scoped>
.settings {
  max-width: 900px;
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

.theme-section {
  padding: 10px 0;
}

.theme-list {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.theme-card {
  width: 180px;
  cursor: pointer;
  position: relative;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 8px;
  transition: all 0.3s;
}

.theme-card:hover {
  border-color: #409eff;
}

.theme-card.active {
  border-color: #409eff;
}

.theme-preview {
  width: 100%;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  background: var(--bg);
}

.preview-sidebar {
  width: 30px;
  background: var(--sidebar);
}

.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-header {
  height: 20px;
  background: var(--header);
}

.preview-body {
  flex: 1;
  background: var(--bg);
}

.theme-name {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
}

.theme-check {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #409eff;
  font-size: 20px;
}
</style>
