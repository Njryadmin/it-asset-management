<template>
  <div class="settings-page">
    <!-- Header -->
    <div class="settings-header">
      <div class="header-left">
        <h2 class="page-title">系统设置</h2>
        <p class="page-desc">管理站点信息、主题外观和系统配置</p>
      </div>
      <div class="header-right">
        <el-button :icon="View" text @click="showLoginPreview = true">登录预览</el-button>
        <el-button :icon="Monitor" text @click="showThemePreview = true">主题预览</el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="settings-tabs" tab-position="top">
      <!-- Tab 1: 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="tab-content">
          <!-- 站点信息 -->
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><Monitor /></el-icon>
                <span>站点信息</span>
              </div>
            </template>
            <el-form label-position="top" class="settings-form">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="站点名称">
                    <el-input v-model="form.site_name" placeholder="例如：IT资产管理系统" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="资产编号前缀">
                    <el-input v-model="form.asset_code_prefix" placeholder="例如 ASSET" clearable />
                    <div class="field-hint">编号示例：{{ assetCodeExample }}</div>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="站点描述">
                    <el-input v-model="form.site_description" type="textarea" :rows="2" placeholder="简要描述系统用途" clearable />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 品牌标识 -->
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><Picture /></el-icon>
                <span>品牌标识</span>
              </div>
            </template>
            <div class="brand-upload-row">
              <div class="brand-upload-item">
                <div class="brand-upload-label">站点 Logo</div>
                <div class="brand-upload-box" @click="triggerLogoUpload">
                  <img v-if="tempLogoUrl" :src="tempLogoUrl" alt="logo" class="brand-preview-img" />
                  <div v-else class="brand-placeholder">
                    <el-icon :size="28"><Picture /></el-icon>
                    <span>点击上传</span>
                  </div>
                </div>
                <div class="brand-upload-hint">建议 200×60px，支持 PNG/JPG/SVG</div>
                <input ref="logoInputRef" type="file" accept="image/*" style="display:none" @change="onLogoFileChange" />
              </div>
              <div class="brand-upload-item">
                <div class="brand-upload-label">浏览器图标</div>
                <div class="brand-upload-box brand-upload-box--sm" @click="triggerFaviconUpload">
                  <img v-if="tempFaviconUrl" :src="tempFaviconUrl" alt="favicon" class="brand-favicon-preview" />
                  <div v-else class="brand-placeholder">
                    <el-icon :size="20"><Picture /></el-icon>
                    <span>上传</span>
                  </div>
                </div>
                <div class="brand-upload-hint">建议 32×32px</div>
                <input ref="faviconInputRef" type="file" accept="image/*" style="display:none" @change="onFaviconFileChange" />
              </div>
            </div>
          </el-card>

          <!-- 联系方式 -->
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><Message /></el-icon>
                <span>联系方式</span>
              </div>
            </template>
            <el-form label-position="top" class="settings-form">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="公司名称">
                    <el-input v-model="form.company_name" placeholder="显示在登录页底部" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="联系电话">
                    <el-input v-model="form.contact_phone" placeholder="显示在登录页底部" clearable />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="联系邮箱">
                    <el-input v-model="form.contact_email" placeholder="显示在登录页底部" clearable />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <div class="form-actions">
            <el-button @click="fetchSettings">重置</el-button>
            <el-button type="primary" :loading="savingSite" @click="saveSiteInfo">保存更改</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 2: 主题 -->
      <el-tab-pane label="主题" name="theme">
        <div class="tab-content">
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><Brush /></el-icon>
                <span>界面主题</span>
              </div>
            </template>
            <div class="theme-grid">
              <div
                v-for="(theme, key) in themeList"
                :key="String(key)"
                class="theme-card"
                :class="{ active: currentTheme === String(key) }"
                @click="handleSelectTheme(String(key))"
              >
                <div class="theme-preview">
                  <div class="preview-sidebar" :style="{ background: theme.sidebar_color }"></div>
                  <div class="preview-content">
                    <div class="preview-header" :style="{ background: theme.header_color }">
                      <div class="preview-dot" :style="{ background: theme.primary }"></div>
                    </div>
                    <div class="preview-body" :style="{ background: theme.bg_color }">
                      <div class="preview-line" :style="{ background: theme.border_color }"></div>
                      <div class="preview-line short" :style="{ background: theme.border_color }"></div>
                    </div>
                  </div>
                </div>
                <div class="theme-footer">
                  <span class="theme-name">{{ theme.name }}</span>
                  <el-tag v-if="currentTheme === String(key)" type="success" size="small">使用中</el-tag>
                </div>
              </div>
            </div>
            <div class="theme-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>主题切换实时生效，无需保存</span>
            </div>
          </el-card>

          <!-- 内联登录预览 -->
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><View /></el-icon>
                <span>登录页预览</span>
              </div>
            </template>
            <div class="inline-login-preview">
              <div class="ilp-logo-area" :style="{ background: previewPrimary }">
                <img v-if="tempLogoUrl" :src="tempLogoUrl" alt="logo" class="ilp-logo" />
                <span v-else class="ilp-logo-text">{{ form.site_name || '系统名称' }}</span>
              </div>
              <div class="ilp-body">
                <div class="ilp-title">{{ form.site_name || '站点名称' }}</div>
                <div class="ilp-desc">{{ form.site_description || '简要描述系统用途' }}</div>
                <div class="ilp-form">
                  <div class="ilp-input"><span>请输入用户名</span></div>
                  <div class="ilp-input"><span>请输入密码</span></div>
                  <div class="ilp-btn" :style="{ background: previewPrimary }">登 录</div>
                </div>
                <div class="ilp-footer">
                  <span>{{ form.site_name || 'IT资产管理系统' }}</span>
                  <span v-if="form.company_name"> · {{ form.company_name }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 备份设置 -->
      <el-tab-pane label="备份设置" name="backup">
        <div class="tab-content">
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><FolderOpened /></el-icon>
                <span>数据备份</span>
              </div>
            </template>
            <el-form label-position="top" class="settings-form">
              <el-form-item>
                <div class="switch-row">
                  <div>
                    <div class="switch-label">自动备份</div>
                    <div class="switch-hint">开启后系统将自动定期备份数据</div>
                  </div>
                  <el-switch v-model="form.auto_backup" />
                </div>
              </el-form-item>
              <el-form-item v-if="form.auto_backup" label="备份保留天数">
                <el-input-number v-model="form.backup_retention_days" :min="1" :max="365" />
                <div class="field-hint">超过此天数的备份将自动清理</div>
              </el-form-item>
            </el-form>
            <div class="form-actions">
              <el-button @click="fetchSettings">重置</el-button>
              <el-button type="primary" :loading="savingBasic" @click="saveBasic">保存更改</el-button>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Tab 4: 公告 -->
      <el-tab-pane label="公告" name="announcement">
        <div class="tab-content">
          <el-card class="settings-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon class="card-header-icon"><Bell /></el-icon>
                <span>系统公告</span>
              </div>
            </template>
            <el-form label-position="top" class="settings-form">
              <el-form-item>
                <div class="switch-row">
                  <div>
                    <div class="switch-label">启用公告</div>
                    <div class="switch-hint">开启后登录页顶部将显示公告内容</div>
                  </div>
                  <el-switch v-model="form.announcement_enabled" />
                </div>
              </el-form-item>
              <el-form-item v-if="form.announcement_enabled" label="公告内容">
                <el-input v-model="form.announcement" type="textarea" :rows="4" placeholder="输入公告内容" clearable />
              </el-form-item>
            </el-form>
            <div class="form-actions">
              <el-button @click="fetchSettings">重置</el-button>
              <el-button type="primary" :loading="savingAnnouncement" @click="saveAnnouncement">保存更改</el-button>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Login Preview Drawer -->
    <el-drawer v-model="showLoginPreview" title="登录页预览" size="380px" direction="rtl">
      <div class="drawer-preview">
        <div class="dp-header" :style="{ background: previewPrimary }">
          <img v-if="tempLogoUrl" :src="tempLogoUrl" alt="logo" class="dp-logo" />
          <span v-else class="dp-logo-text">{{ form.site_name || '系统名称' }}</span>
        </div>
        <div class="dp-body">
          <div class="dp-title">{{ form.site_name || '站点名称' }}</div>
          <div class="dp-desc">{{ form.site_description || '简要描述系统用途' }}</div>
          <div class="dp-form">
            <div class="dp-input"><span>请输入用户名</span></div>
            <div class="dp-input"><span>请输入密码</span></div>
            <div class="dp-btn" :style="{ background: previewPrimary }">登 录</div>
          </div>
        </div>
        <div class="dp-footer">
          <span>{{ form.site_name || 'IT资产管理系统' }}</span>
          <span v-if="form.contact_phone"> · {{ form.contact_phone }}</span>
          <span v-if="form.contact_email"> · {{ form.contact_email }}</span>
          <span v-if="form.company_name"> · {{ form.company_name }}</span>
        </div>
      </div>
    </el-drawer>

    <!-- Theme Preview Drawer -->
    <el-drawer v-model="showThemePreview" title="主题预览" size="500px" direction="rtl">
      <div class="theme-detail-preview">
        <div class="tdp-sidebar" :style="{ background: currentThemeData.sidebar_color }">
          <div class="tdp-nav-item" :style="{ color: currentThemeData.sidebar_active_icon || currentThemeData.sidebar_text, background: currentThemeData.sidebar_active_bg }">
            <div class="tdp-nav-dot" :style="{ background: currentThemeData.primary }"></div>
            <span>资产</span>
          </div>
          <div class="tdp-nav-item" :style="{ color: currentThemeData.sidebar_text }">
            <div class="tdp-nav-dot" :style="{ background: currentThemeData.sidebar_text }"></div>
            <span>采购</span>
          </div>
          <div class="tdp-nav-item" :style="{ color: currentThemeData.sidebar_text }">
            <div class="tdp-nav-dot" :style="{ background: currentThemeData.sidebar_text }"></div>
            <span>审批</span>
          </div>
        </div>
        <div class="tdp-main" :style="{ background: currentThemeData.bg_color }">
          <div class="tdp-topbar" :style="{ background: currentThemeData.header_color, borderBottom: `1px solid ${currentThemeData.border_color}` }">
            <div class="tdp-breadcrumb" :style="{ color: currentThemeData.text_secondary }">首页</div>
            <div class="tdp-user" :style="{ background: currentThemeData.primary }"></div>
          </div>
          <div class="tdp-content" style="padding: 16px">
            <div class="tdp-card" :style="{ background: currentThemeData.card_bg, border: `1px solid ${currentThemeData.border_light || currentThemeData.border_color}`, borderRadius: '8px', padding: '16px' }">
              <div :style="{ color: currentThemeData.text_primary, fontWeight: '600', fontSize: '15px' }">{{ form.site_name || '资产管理系统' }}</div>
              <div :style="{ color: currentThemeData.text_secondary, fontSize: '12px', marginTop: '4px' }">共 {{ form.asset_code_prefix || 'ASSET' }}-{{ new Date().getFullYear() }}-000001 条记录</div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>


<script setup lang="ts">

import { ref, reactive, computed, onMounted } from 'vue'
import { settingsApi } from '@/api/settings'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import {
  Check, Plus, Picture, RefreshRight, Setting, Brush, Bell,
  View, Monitor, Phone, Message, Grid, Sunny
} from '@element-plus/icons-vue'

// ── Theme definitions ──
const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.isSuperuser === true)

const themeList: Record<string, any> = {
  default: {
    name: '默认主题',
    primary: '#3B82F6',
    bg_color: '#F1F5F9',
    bg_color_secondary: '#E8EDF3',
    sidebar_color: 'rgba(255, 255, 255, 0.95)',
    sidebar_text: '#475569',
    sidebar_active_bg: 'rgba(59, 130, 246, 0.1)',
    sidebar_active_icon: '#3B82F6',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#0F172A',
    text_secondary: '#475569',
    border_color: '#E2E8F0',
    border_light: '#F1F5F9',
  },
  dark: {
    name: '深色主题',
    primary: '#3B82F6',
    bg_color: '#09090B',
    bg_color_secondary: '#111113',
    sidebar_color: 'rgba(16, 16, 18, 0.92)',
    sidebar_text: '#A1A1AA',
    sidebar_active_bg: 'rgba(59, 130, 246, 0.12)',
    sidebar_active_icon: '#3B82F6',
    header_color: 'rgba(16, 16, 18, 0.88)',
    card_bg: 'rgba(24, 24, 27, 0.85)',
    text_primary: '#FAFAFA',
    text_secondary: '#A1A1AA',
    border_color: 'rgba(255, 255, 255, 0.08)',
    border_light: 'rgba(255, 255, 255, 0.05)',
  }
}

// ── State ──
const currentTheme = ref(localStorage.getItem('app-theme') || 'default')
const currentThemeData = computed(() => themeList[currentTheme.value] || themeList.default)
const previewPrimary = computed(() => currentThemeData.value.primary)

const savingSite = ref(false)
const savingBasic = ref(false)
const savingAnnouncement = ref(false)

// ── Tab & Drawer state ──
const activeTab = ref('basic')
const showLoginPreview = ref(false)
const showThemePreview = ref(false)

// ── Form Data ──
const form = reactive({
  site_name: '',
  site_description: '',
  company_name: '',
  contact_email: '',
  contact_phone: '',
  asset_code_prefix: 'ASSET',
  auto_backup: true,
  backup_retention_days: 30,
  logo_url: '',
  favicon_url: '',
  announcement: '',
  announcement_enabled: false
})

// ── Temp state for previews before save ──
const tempLogoUrl = ref('')
const tempFaviconUrl = ref('')

// ── File input refs ──
const logoInputRef = ref<HTMLInputElement>()
const faviconInputRef = ref<HTMLInputElement>()

// ── Computed ──
const assetCodeExample = computed(() => {
  const prefix = form.asset_code_prefix || 'ASSET'
  const year = new Date().getFullYear()
  return `${prefix}-${year}-000001`
})

// ── Logo / Favicon upload ──
function triggerLogoUpload() {
  logoInputRef.value?.click()
}

function triggerFaviconUpload() {
  faviconInputRef.value?.click()
}

function onLogoFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    tempLogoUrl.value = ev.target?.result as string
  }
  reader.readAsDataURL(file)
  uploadLogo(file)
}

function onFaviconFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    tempFaviconUrl.value = ev.target?.result as string
  }
  reader.readAsDataURL(file)
  uploadFavicon(file)
}

async function uploadLogo(file: File) {
  try {
    const res = await settingsApi.uploadLogo(file)
    form.logo_url = res.data.url
    ElMessage.success('LOGO 上传成功')
  } catch {
    ElMessage.error('LOGO 上传失败')
  }
}

async function uploadFavicon(file: File) {
  try {
    const res = await settingsApi.uploadFavicon(file)
    form.favicon_url = res.data.url
    ElMessage.success('图标上传成功')
  } catch {
    ElMessage.error('图标上传失败')
  }
}

// ── Fetch settings ──
async function fetchSettings() {
  try {
    const res: any = await settingsApi.get()
    const d = res.data as any
    form.site_name = d.systemName || ''
    form.site_description = d.siteDescription || ''
    form.company_name = d.companyName || ''
    form.contact_email = d.contactEmail || ''
    form.contact_phone = d.contactPhone || ''
    form.asset_code_prefix = d.assetCodePrefix || 'ASSET'
    form.auto_backup = d.autoBackup ?? true
    form.backup_retention_days = d.backupRetentionDays || 30
    form.logo_url = d.logoUrl || ''
    form.favicon_url = d.faviconUrl || ''
    form.announcement = d.announcement || ''
    form.announcement_enabled = d.announcementEnabled ?? false
    tempLogoUrl.value = d.logoUrl || ''
    tempFaviconUrl.value = d.faviconUrl || ''
  } catch {
    ElMessage.error('获取设置失败')
  }
}

// ── Save handlers ──
async function saveSiteInfo() {
  savingSite.value = true
  try {
    await settingsApi.update({
      system_name: form.site_name,
      site_description: form.site_description,
      company_name: form.company_name,
      contact_email: form.contact_email,
      contact_phone: form.contact_phone,
      logo_url: form.logo_url,
      favicon_url: form.favicon_url
    })
    ElMessage.success('站点信息已保存')
  } catch {
    // handled by interceptor
  } finally {
    savingSite.value = false
  }
}

async function saveBasic() {
  savingBasic.value = true
  try {
    await settingsApi.update({
      asset_code_prefix: form.asset_code_prefix,
      company_name: form.company_name,
      contact_email: form.contact_email,
      contact_phone: form.contact_phone,
      auto_backup: form.auto_backup,
      backup_retention_days: form.backup_retention_days
    })
    ElMessage.success('基础设置已保存')
  } catch {
    // handled by interceptor
  } finally {
    savingBasic.value = false
  }
}

// ── Cancel handlers ──
function cancelSiteInfo() {
  fetchSettings()
}

function cancelBasic() {
  fetchSettings()
}

async function saveAnnouncement() {
  savingAnnouncement.value = true
  try {
    await settingsApi.update({
      announcement: form.announcement,
      announcement_enabled: form.announcement_enabled
    })
    ElMessage.success('公告设置已保存')
  } catch {
    // handled by interceptor
  } finally {
    savingAnnouncement.value = false
  }
}

function cancelAnnouncement() {
  fetchSettings()
}

// ── Theme switcher ──
function handleSelectTheme(key: string) {
  currentTheme.value = key
  const theme = themeList[key]
  if (!theme) return

  const root = document.documentElement
  root.style.setProperty('--wechat-primary', theme.primary)
  root.style.setProperty('--wechat-bg', theme.bg_color)
  root.style.setProperty('--wechat-bg-secondary', theme.bg_color_secondary || theme.bg_color)
  root.style.setProperty('--wechat-card', theme.card_bg)
  root.style.setProperty('--wechat-text', theme.text_primary)
  root.style.setProperty('--wechat-text-secondary', theme.text_secondary)
  root.style.setProperty('--wechat-border', theme.border_color)
  root.style.setProperty('--wechat-border-light', theme.border_light)
  root.style.setProperty('--wechat-sidebar', theme.sidebar_color)
  root.style.setProperty('--wechat-sidebar-text', theme.sidebar_text)
  root.style.setProperty('--wechat-sidebar-active-bg', theme.sidebar_active_bg)
  root.style.setProperty('--wechat-shadow', '0 2px 8px rgba(0,0,0,0.08)')
  root.style.setProperty('--wechat-shadow-hover', '0 4px 16px rgba(0,0,0,0.12)')
  root.style.setProperty('--el-color-primary', theme.primary)
  root.style.setProperty('--el-bg-color', theme.bg_color)
  root.style.setProperty('--el-bg-color-page', theme.bg_color)
  root.style.setProperty('--el-bg-color-overlay', theme.card_bg)
  root.style.setProperty('--el-text-color-primary', theme.text_primary)
  root.style.setProperty('--el-text-color-regular', theme.text_secondary)
  root.style.setProperty('--el-border-color', theme.border_color)
  root.style.setProperty('--el-fill-color-blank', theme.card_bg)

  root.setAttribute('data-theme', key)
  if (key === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
  document.body.style.backgroundColor = theme.bg_color
  localStorage.setItem('app-theme', key)

  ElMessage.success(`已切换到「${theme.name}」`)
}

onMounted(() => {
  fetchSettings()
  if (currentTheme.value && currentTheme.value !== 'default') {
    handleSelectTheme(currentTheme.value)
  }
})

</script>

<style scoped>

/* ── Page Layout ── */
.settings-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
}

.page-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

/* ── Settings Cards ── */
.settings-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card);
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.site-icon { background: linear-gradient(135deg, #3B82F6, #2563EB); }
.basic-icon { background: linear-gradient(135deg, #FF991A, #FFB84D); }
.theme-icon { background: linear-gradient(135deg, var(--primary), var(--primary-hover, #2563EB)); }

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0;
}

.card-body {
  padding: 22px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  padding: 14px 22px;
  border-top: 1px solid var(--border);
  background: var(--bg-page);
}

/* ── Upload Zone ── */
.upload-row {
  display: flex;
  gap: 24px;
  margin-bottom: 22px;
}

.upload-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  display: block;
}

.upload-zone {
  width: 200px;
  height: 80px;
  border: 1.5px dashed var(--border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  overflow: hidden;
  position: relative;
  transition: all var(--transition-fast);
  background: var(--bg-page);
}

.upload-zone:hover {
  border-color: var(--primary);
  background: var(--primary-bg);
}

.upload-zone.has-image {
  border-style: solid;
  border-color: var(--primary);
}

.favicon-zone {
  width: 80px;
  height: 80px;
  overflow: hidden;
  border-radius: var(--radius-md);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 4px;
}

.upload-icon {
  font-size: 22px;
  color: var(--text-muted);
}

.upload-text {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.upload-meta {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-hint {
  font-size: 11px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
}

.hint-tag {
  background: var(--bg-hover);
  color: var(--text-secondary);
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 500;
  flex-shrink: 0;
}

.upload-format {
  font-size: 11px;
  color: var(--text-muted);
}

.preview-overlay {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 6px;
}

.favicon-preview {
  object-fit: contain;
  border-radius: var(--radius-sm);
}

/* Logo 侧边栏预览 */
.logo-preview-bar {
  margin-top: 12px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
}

.logo-preview-label {
  font-size: 10px;
  color: var(--text-muted);
  padding: 4px 8px;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
}

.logo-preview-sidebar {
  height: 52px;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  padding: 0 12px;
}

.logo-preview-img {
  width: 100%;
  max-height: 36px;
  object-fit: contain;
}

/* Favicon 浏览器标签预览 */
.favicon-preview-bar {
  margin-top: 12px;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
}

.browser-tab {
  height: 36px;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  border-bottom: 1px solid var(--border);
}

.browser-tab-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

.browser-tab-title {
  font-size: 12px;
  color: var(--text-primary);
  font-weight: 500;
}

.preview-mask {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
  font-size: 12px;
}

.preview-mask .el-icon {
  font-size: 18px;
}

.upload-zone:hover .preview-mask {
  opacity: 1;
}

/* ── Form ── */
.compact-form .el-form-item {
  margin-bottom: 16px;
}

.prefix-input-group {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.prefix-example {
  display: flex;
  align-items: center;
  gap: 8px;
}

.prefix-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.inline-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 16px;
}

.switch-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.switch-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.backup-days-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.days-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* ── Theme Grid ── */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.theme-card {
  border: 2px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s;
  position: relative;
}

.theme-card:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.theme-card.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.theme-preview {
  height: 100px;
  display: flex;
  overflow: hidden;
}

.preview-sidebar {
  width: 28px;
  flex-shrink: 0;
}

.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-header {
  height: 22px;
  display: flex;
  align-items: center;
  padding: 0 8px;
}

.preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.preview-body {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.preview-line {
  height: 6px;
  border-radius: 3px;
  opacity: 0.6;
}

.preview-line.short {
  width: 60%;
}

.theme-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: var(--bg-page);
}

.theme-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.theme-check {
  color: var(--primary);
  font-size: 16px;
}

.theme-active-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--primary);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

/* ── Preview Sidebar ── */
.settings-sidebar {
  position: sticky;
  top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.preview-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
  background: var(--bg-page);
}

/* Login Preview */
.login-preview {
  overflow: hidden;
}

.login-preview-header {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.login-logo img {
  max-height: 48px;
  max-width: 160px;
  object-fit: contain;
}

.login-logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.login-preview-body {
  padding: 20px;
  background: var(--bg-card);
}

.login-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.login-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 16px;
  line-height: 1.5;
}

.login-form-preview {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.login-input {
  height: 34px;
  background: var(--bg-page);
  border-radius: 6px;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 10px;
  gap: 6px;
  font-size: 12px;
  color: var(--text-placeholder);
}

.login-input::before {
  content: '';
  width: 14px;
  height: 14px;
  border: 1.5px solid var(--border-color);
  border-radius: 3px;
  flex-shrink: 0;
}

.login-input:last-of-type::before {
  border-radius: 50%;
}

.login-input-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-btn {
  height: 36px;
  border-radius: 6px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  letter-spacing: 2px;
}

/* Theme Detail Preview */
.theme-detail-preview {
  display: flex;
  height: 180px;
  overflow: hidden;
}

.tdp-sidebar {
  width: 56px;
  flex-shrink: 0;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tdp-nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  font-size: 11px;
  cursor: default;
}

.tdp-nav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.tdp-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tdp-topbar {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  flex-shrink: 0;
}

.tdp-breadcrumb {
  font-size: 11px;
}

.tdp-user {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.tdp-content {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tdp-card {
  border-radius: 6px;
  padding: 10px;
  flex: 1;
}

.tdp-card-title {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
}

.tdp-card-meta {
  font-size: 10px;
}

/* ── Animations ── */
.anim-fade-in-up {
  animation: fadeInUp 0.35s ease both;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  .settings-sidebar {
    position: static;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}

@media (max-width: 640px) {
  .settings-page {
    padding: 16px 12px;
  }
  .upload-row {
    flex-direction: column;
  }
  .upload-zone {
    width: 100% !important;
  }
  .inline-fields {
    grid-template-columns: 1fr;
  }
  .settings-sidebar {
    grid-template-columns: 1fr;
  }
  .theme-grid {
    grid-template-columns: 1fr;
  }
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .settings-page { padding: 12px 10px; }
  .settings-grid { grid-template-columns: 1fr; }
  .settings-sidebar { grid-template-columns: 1fr 1fr; gap: 12px; }
  .settings-sidebar .settings-nav-card { padding: 14px 12px; }
}


/* ── New Settings Layout ── */
.settings-page {
  padding: 24px;
  min-height: 100vh;
}
.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  gap: 16px;
}
.page-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.page-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}
.header-right {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.settings-tabs {
  --el-tabs-header-height: 44px;
}
.settings-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
}
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}
.tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  margin-top: 8px;
}
.settings-card {
  border-radius: 12px;
  border: 1px solid var(--border);
}
.settings-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-light);
  background: transparent;
}
.settings-card :deep(.el-card__body) {
  padding: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.card-header-icon {
  font-size: 16px;
  color: var(--primary-color, #3B82F6);
}
.settings-form {
  margin: 0;
}
.settings-form :deep(.el-form-item) {
  margin-bottom: 16px;
}
.settings-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}
.settings-form :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  padding-bottom: 6px !important;
}
.field-hint {
  font-size: 12px;
  color: var(--text-placeholder);
  margin-top: 4px;
  line-height: 1.4;
}
.brand-upload-row {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}
.brand-upload-item {
  flex: 1;
}
.brand-upload-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.brand-upload-box {
  width: 200px;
  height: 80px;
  border: 1.5px dashed var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s;
  overflow: hidden;
  background: var(--bg-page);
}
.brand-upload-box:hover {
  border-color: var(--primary-color, #3B82F6);
}
.brand-upload-box--sm {
  width: 64px;
  height: 64px;
}
.brand-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-placeholder);
  font-size: 12px;
}
.brand-preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.brand-favicon-preview {
  width: 40px;
  height: 40px;
  object-fit: contain;
}
.brand-upload-hint {
  font-size: 12px;
  color: var(--text-placeholder);
  margin-top: 6px;
}
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.switch-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
.switch-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}
.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.theme-card {
  border: 2px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.theme-card:hover {
  border-color: var(--primary-color, #3B82F6);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.theme-card.active {
  border-color: var(--primary-color, #3B82F6);
}
.theme-preview {
  display: flex;
  height: 100px;
}
.preview-sidebar {
  width: 28px;
  flex-shrink: 0;
}
.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.preview-header {
  height: 20px;
  display: flex;
  align-items: center;
  padding: 0 6px;
  gap: 4px;
}
.preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.preview-body {
  flex: 1;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.preview-line {
  height: 4px;
  border-radius: 2px;
  opacity: 0.6;
}
.preview-line.short {
  width: 60%;
}
.theme-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--bg-page);
}
.theme-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
.theme-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 12px;
  padding: 8px 12px;
  background: var(--bg-page);
  border-radius: 6px;
}
.inline-login-preview {
  width: 100%;
  max-width: 360px;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.ilp-logo-area {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}
.ilp-logo {
  max-height: 48px;
  max-width: 160px;
  object-fit: contain;
}
.ilp-logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}
.ilp-body {
  background: var(--card-bg);
  padding: 20px;
}
.ilp-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.ilp-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  line-height: 1.5;
}
.ilp-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ilp-input {
  height: 32px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  font-size: 12px;
  color: var(--text-placeholder);
}
.ilp-btn {
  height: 34px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  letter-spacing: 2px;
  margin-top: 4px;
}
.ilp-footer {
  font-size: 11px;
  color: var(--text-placeholder);
  text-align: center;
  margin-top: 14px;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 8px 0;
}
.drawer-preview {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.dp-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
}
.dp-logo {
  max-height: 48px;
  max-width: 160px;
  object-fit: contain;
}
.dp-logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}
.dp-body {
  background: var(--card-bg);
  padding: 20px;
}
.dp-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.dp-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 14px;
  line-height: 1.5;
}
.dp-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.dp-input {
  height: 32px;
  background: var(--bg-page);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  font-size: 12px;
  color: var(--text-placeholder);
}
.dp-btn {
  height: 34px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  letter-spacing: 2px;
  margin-top: 4px;
}
.dp-footer {
  font-size: 11px;
  color: var(--text-placeholder);
  text-align: center;
  padding: 14px 20px;
  border-top: 1px solid var(--border-light);
}
.theme-detail-preview {
  display: flex;
  height: 260px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.tdp-sidebar {
  width: 56px;
  flex-shrink: 0;
  padding: 8px 0;
}
.tdp-nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  font-size: 11px;
}
.tdp-nav-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.tdp-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.tdp-topbar {
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
}
.tdp-breadcrumb {
  font-size: 11px;
}
.tdp-user {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}
.tdp-content {
  flex: 1;
  overflow: hidden;
}

</style>
