<template>
  <div class="settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <h2 class="page-title">系统设置</h2>
      <p class="page-desc">管理站点基本信息、资产配置和界面主题</p>
    </div>

    <div class="settings-grid">
      <!-- Left Column -->
      <div class="settings-main">

        <!-- 站点信息卡片 - 仅管理员可见 -->
        <div v-if="isAdmin" class="settings-card anim-fade-in-up">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon site-icon">
                <el-icon><Grid /></el-icon>
              </div>
              <div>
                <h3 class="card-title">站点信息</h3>
                <p class="card-subtitle">配置站点名称、描述和品牌标识</p>
              </div>
            </div>
          </div>

          <div class="card-body">
            <!-- Logo & Favicon Row -->
            <div class="upload-row">
              <!-- Logo Upload -->
              <div class="upload-item">
                <span class="upload-label">站点 LOGO</span>
                <div class="upload-zone logo-zone" :class="{ 'has-image': tempLogoUrl }" @click="triggerLogoUpload">
                  <input ref="logoInputRef" type="file" accept="image/*" hidden @change="onLogoFileChange" />
                  <div v-if="tempLogoUrl" class="preview-overlay">
                    <img :src="tempLogoUrl" class="preview-img" alt="LOGO预览" />
                    <div class="preview-mask">
                      <el-icon><RefreshRight /></el-icon>
                      <span>重新上传</span>
                    </div>
                  </div>
                  <div v-else class="upload-placeholder">
                    <el-icon class="upload-icon"><Plus /></el-icon>
                    <span class="upload-text">上传LOGO</span>
                  </div>
                </div>
                <div class="upload-meta">
                  <span class="upload-hint">
                    <span class="hint-tag">建议尺寸</span>
                    宽 220 × 高 44 像素（等比例）
                  </span>
                  <span class="upload-hint">
                    <span class="hint-tag">实际显示</span>
                    侧边栏宽度自适应，高度固定 44px
                  </span>
                  <span class="upload-format">支持 PNG · JPG · SVG</span>
                </div>
                <!-- Logo 侧边栏预览 -->
                <div v-if="tempLogoUrl" class="logo-preview-bar">
                  <div class="logo-preview-label">侧边栏预览效果</div>
                  <div class="logo-preview-sidebar">
                    <img :src="tempLogoUrl" class="logo-preview-img" alt="logo" />
                  </div>
                </div>
              </div>

              <!-- Favicon Upload -->
              <div class="upload-item">
                <span class="upload-label">站点图标</span>
                <div class="upload-zone favicon-zone" :class="{ 'has-image': tempFaviconUrl }" @click="triggerFaviconUpload">
                  <input ref="faviconInputRef" type="file" accept="image/*" hidden @change="onFaviconFileChange" />
                  <div v-if="tempFaviconUrl" class="preview-overlay">
                    <img :src="tempFaviconUrl" class="preview-img favicon-preview" alt="图标预览" />
                    <div class="preview-mask">
                      <el-icon><RefreshRight /></el-icon>
                      <span>重新上传</span>
                    </div>
                  </div>
                  <div v-else class="upload-placeholder">
                    <el-icon class="upload-icon"><Picture /></el-icon>
                    <span class="upload-text">上传图标</span>
                  </div>
                </div>
                <div class="upload-meta">
                  <span class="upload-hint">
                    <span class="hint-tag">建议尺寸</span>
                    32 × 32 像素（正方形）
                  </span>
                  <span class="upload-hint">
                    <span class="hint-tag">实际显示</span>
                    浏览器标签 · 32×32px
                  </span>
                  <span class="upload-format">支持 PNG · ICO · SVG</span>
                </div>
                <!-- Favicon 浏览器标签预览 -->
                <div v-if="tempFaviconUrl" class="logo-preview-bar">
                  <div class="logo-preview-label">浏览器标签预览效果</div>
                  <div class="favicon-preview-bar">
                    <div class="browser-tab">
                      <img v-if="tempFaviconUrl" :src="tempFaviconUrl" class="browser-tab-icon" alt="favicon" />
                      <span class="browser-tab-title">{{ form.site_name || 'IT资产管理系统' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Form Fields -->
            <el-form label-position="top" class="compact-form">
              <el-form-item label="站点名称">
                <el-input
                  v-model="form.site_name"
                  placeholder="例如：IT资产管理系统"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Monitor /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="站点描述">
                <el-input
                  v-model="form.site_description"
                  type="textarea"
                  :rows="3"
                  placeholder="简要描述系统用途"
                  clearable
                />
              </el-form-item>
            </el-form>
          </div>

          <div class="card-footer">
            <el-button @click="cancelSiteInfo">取消</el-button>
            <el-button type="primary" :loading="savingSite" @click="saveSiteInfo">
              <el-icon v-if="!savingSite"><Check /></el-icon>
              保存站点信息
            </el-button>
          </div>
        </div>

        <!-- 基础设置卡片 - 仅管理员可见 -->
        <div v-if="isAdmin" class="settings-card anim-fade-in-up" style="animation-delay: 80ms">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon basic-icon">
                <el-icon><Setting /></el-icon>
              </div>
              <div>
                <h3 class="card-title">基础设置</h3>
                <p class="card-subtitle">资产编号规则和其他系统参数</p>
              </div>
            </div>
          </div>

          <div class="card-body">
            <el-form label-position="top" class="compact-form">
              <el-form-item label="资产代码前缀">
                <div class="prefix-input-group">
                  <el-input
                    v-model="form.asset_code_prefix"
                    placeholder="例如 ASSET"
                    style="width: 200px"
                    clearable
                  />
                  <div class="prefix-example">
                    <span class="prefix-label">编号示例：</span>
                    <el-tag type="info" effect="plain">{{ assetCodeExample }}</el-tag>
                  </div>
                </div>
              </el-form-item>

              <el-form-item label="公司名称">
                <el-input
                  v-model="form.company_name"
                  placeholder="请输入公司名称"
                  clearable
                >
                  <template #prefix>
                    <el-icon><Sunny /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <div class="inline-fields">
                <el-form-item label="联系电话">
                  <el-input
                    v-model="form.contact_phone"
                    placeholder="请输入联系电话"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Phone /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="联系邮箱">
                  <el-input
                    v-model="form.contact_email"
                    placeholder="请输入联系邮箱"
                    clearable
                  >
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <el-form-item label="自动备份">
                <div class="switch-row">
                  <el-switch v-model="form.auto_backup" />
                  <span class="switch-desc">开启后系统将按计划自动备份数据</span>
                </div>
              </el-form-item>

              <el-form-item v-if="form.auto_backup" label="备份保留天数">
                <div class="backup-days-group">
                  <el-input-number
                    v-model="form.backup_retention_days"
                    :min="1"
                    :max="365"
                    :step="1"
                  />
                  <span class="days-desc">天，逾期备份将自动清理</span>
                </div>
              </el-form-item>
            </el-form>
          </div>

          <div class="card-footer">
            <el-button @click="cancelBasic">取消</el-button>
            <el-button type="primary" :loading="savingBasic" @click="saveBasic">
              <el-icon v-if="!savingBasic"><Check /></el-icon>
              保存基础设置
            </el-button>
          </div>
        </div>

        <!-- 公告设置卡片 -->
        <div class="settings-card anim-fade-in-up" style="animation-delay: 120ms">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon theme-icon">
                <el-icon><Bell /></el-icon>
              </div>
              <div>
                <h3 class="card-title">公告设置</h3>
                <p class="card-subtitle">在仪表盘顶部显示滚动公告信息</p>
              </div>
            </div>
          </div>
          <div class="card-body">
            <el-form label-position="top">
              <el-form-item label="启用公告">
                <div class="switch-row">
                  <el-switch v-model="form.announcement_enabled" />
                  <span class="switch-desc">开启后仪表盘顶部将显示滚动公告</span>
                </div>
              </el-form-item>

              <el-form-item v-if="form.announcement_enabled" label="公告内容">
                <el-input
                  v-model="form.announcement"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入公告内容，例如：本周系统将于周六22:00-23:00进行维护升级，届时服务将暂时中断。"
                  clearable
                />
                <div class="form-tip">支持多行文本，将在仪表盘顶部自动滚动显示</div>
              </el-form-item>
            </el-form>
          </div>
          <div class="card-footer">
            <el-button @click="cancelAnnouncement">取消</el-button>
            <el-button type="primary" :loading="savingAnnouncement" @click="saveAnnouncement">
              <el-icon v-if="!savingAnnouncement"><Check /></el-icon>
              保存公告设置
            </el-button>
          </div>
        </div>

        <!-- 主题设置卡片 -->
        <div class="settings-card anim-fade-in-up" style="animation-delay: 160ms">
          <div class="card-header">
            <div class="card-title-group">
              <div class="card-icon theme-icon">
                <el-icon><Brush /></el-icon>
              </div>
              <div>
                <h3 class="card-title">主题设置</h3>
                <p class="card-subtitle">选择适合您的主色调和界面风格</p>
              </div>
            </div>
          </div>

          <div class="card-body">
            <div class="theme-grid">
              <div
                v-for="(theme, key) in themeList"
                :key="String(key)"
                class="theme-card"
                :class="{ active: currentTheme === String(key) }"
                @click="selectTheme(String(key))"
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
                  <el-icon v-if="currentTheme === String(key)" class="theme-check"><Check /></el-icon>
                </div>
                <div v-if="currentTheme === String(key)" class="theme-active-tag">应用中</div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Live Preview -->
      <div class="settings-sidebar">
        <div class="preview-card anim-fade-in-up" style="animation-delay: 120ms">
          <div class="preview-card-header">
            <el-icon><View /></el-icon>
            <span>登录页预览</span>
          </div>
          <div class="login-preview">
            <div class="login-preview-header" :style="{ background: previewPrimary }">
              <div class="login-logo">
                <img v-if="tempLogoUrl" :src="tempLogoUrl" alt="logo" />
                <span v-else class="login-logo-text">{{ form.site_name || '系统名称' }}</span>
              </div>
            </div>
            <div class="login-preview-body">
              <div class="login-title">{{ form.site_name || '站点名称' }}</div>
              <div class="login-desc">{{ form.site_description || '站点描述将显示在这里' }}</div>
              <div class="login-form-preview">
                <div class="login-input"></div>
                <div class="login-input"></div>
                <div class="login-btn" :style="{ background: previewPrimary }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="preview-card anim-fade-in-up" style="animation-delay: 200ms">
          <div class="preview-card-header">
            <el-icon><Monitor /></el-icon>
            <span>主题预览</span>
          </div>
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
            </div>
            <div class="tdp-main" :style="{ background: currentThemeData.bg_color }">
              <div class="tdp-topbar" :style="{ background: currentThemeData.header_color, borderBottom: `1px solid ${currentThemeData.border_color}` }">
                <div class="tdp-breadcrumb" :style="{ color: currentThemeData.text_secondary }">首页</div>
                <div class="tdp-user" :style="{ background: currentThemeData.primary }"></div>
              </div>
              <div class="tdp-content">
                <div class="tdp-card" :style="{ background: currentThemeData.card_bg, border: `1px solid ${currentThemeData.border_light || currentThemeData.border_color}` }">
                  <div class="tdp-card-title" :style="{ color: currentThemeData.text_primary }">{{ form.asset_code_prefix || 'ASSET' }} 资产管理系统</div>
                  <div class="tdp-card-meta" :style="{ color: currentThemeData.text_secondary }">共 {{ form.asset_code_prefix || 'ASSET' }}-2026-000001 条记录</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
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
function selectTheme(key: string) {
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
    selectTheme(currentTheme.value)
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
}

.login-btn {
  height: 36px;
  border-radius: 6px;
  margin-top: 4px;
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

</style>
