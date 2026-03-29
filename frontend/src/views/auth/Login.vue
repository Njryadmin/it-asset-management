<template>
  <div class="login-page" :data-theme="theme">
    <!-- Grid background -->
    <div class="bg-grid"></div>
    <!-- Faint green glow orbs -->
    <div class="bg-glow bg-glow--1"></div>
    <div class="bg-glow bg-glow--2"></div>
    <div class="bg-glow bg-glow--3"></div>

    <div class="login-wrapper">
      <!-- Left brand panel (hidden on mobile) -->
      <div class="brand-panel">
        <div class="brand-panel__grid"></div>
        <div class="brand-panel__content">
          <!-- Logo -->
          <div class="brand-logo">
            <img v-if="settings.logoUrl" :src="settings.logoUrl" alt="Logo" class="brand-logo__img" />
            <svg v-else class="brand-logo__svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="4" y="8" width="40" height="32" rx="4" stroke="currentColor" stroke-width="2.5"/>
              <path d="M4 16h40" stroke="currentColor" stroke-width="2.5"/>
              <circle cx="12" cy="12" r="2" fill="currentColor"/>
              <circle cx="20" cy="12" r="2" fill="currentColor"/>
              <path d="M14 26h8M14 32h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <!-- System name -->
          <h1 class="brand-title">{{ settings.systemName || 'IT资产管理系统' }}</h1>
          <!-- Tagline -->
          <p class="brand-tagline">掌控资产，驱动未来</p>

          <!-- Decorative data viz -->
          <div class="brand-stats">
            <div class="stat-card" v-for="stat in stats" :key="stat.label">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
              <div class="stat-bar">
                <div class="stat-bar__fill" :style="{ width: stat.pct + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- Decorative corner graphic -->
          <div class="brand-corner">
            <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="160" cy="40" r="80" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
              <circle cx="160" cy="40" r="55" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
              <circle cx="160" cy="40" r="30" stroke="currentColor" stroke-width="0.5" opacity="0.15"/>
              <path d="M80 40 Q120 40 160 40" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
              <path d="M160 0 Q160 20 160 40" stroke="currentColor" stroke-width="0.5" opacity="0.2"/>
              <circle cx="160" cy="40" r="4" fill="currentColor" opacity="0.4"/>
              <path d="M40 160 L80 160 L80 120" stroke="currentColor" stroke-width="0.5" opacity="0.15" stroke-linecap="round"/>
              <path d="M120 160 L160 160 L160 120" stroke="currentColor" stroke-width="0.5" opacity="0.15" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Login card -->
      <div class="login-card">
        <div class="login-card__inner">
          <!-- Mobile logo -->
          <div class="mobile-brand">
            <img v-if="settings.logoUrl" :src="settings.logoUrl" alt="Logo" class="mobile-brand__img" />
            <span class="mobile-brand__name">{{ settings.systemName || 'IT资产管理系统' }}</span>
          </div>

          <!-- Header -->
          <div class="login-card__header">
            <div class="login-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z" fill="currentColor"/>
              </svg>
            </div>
            <h1 class="login-greeting">欢迎回来</h1>
            <p class="login-hint">登录到您的账户继续</p>
          </div>

          <!-- Form -->
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-position="top"
            @submit.prevent="handleLogin"
            class="login-form"
          >
            <el-form-item prop="username" class="form-item">
              <el-input
                v-model="form.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                clearable
                class="form-input"
              />
            </el-form-item>

            <el-form-item prop="password" class="form-item">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
                class="form-input"
              />
            </el-form-item>

            <div class="login-options">
              <el-checkbox v-model="form.remember" class="remember-check">
                记住登录状态
              </el-checkbox>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="authStore.loading"
              class="login-button"
              @click="handleLogin"
            >
              <span>登 录</span>
              <svg class="btn-arrow" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 10h12M12 6l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </el-button>
          </el-form>

          <!-- Footer -->
          <div class="login-card__footer">
            <span>{{ settings.systemName || 'IT资产管理系统' }} · {{ settings.version || 'v1.0' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { settingsApi } from '@/api/settings'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const theme = ref<'light' | 'dark'>('light')

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const settings = reactive({
  systemName: 'IT资产管理系统',
  site_title: '',
  siteDescription: '',
  logoUrl: '',
  version: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const stats = [
  { value: '2,847', label: '在册资产', pct: 72 },
  { value: '98.6%', label: '盘点完成率', pct: 98 },
  { value: '156', label: '本月新增', pct: 45 }
]

// Load site settings
onMounted(async () => {
  // Restore remembered credentials
  const savedUsername = localStorage.getItem('remembered_username')
  const savedRemember = localStorage.getItem('remember_me')
  if (savedUsername && savedRemember === 'true') {
    form.username = savedUsername
    form.remember = true
  }

  // Detect theme from document
  const docTheme = document.documentElement.getAttribute('data-theme')
  if (docTheme === 'light') theme.value = 'light'
  else if (docTheme === 'dark') theme.value = 'dark'
  else theme.value = 'dark'

  try {
    const res: any = await settingsApi.get()
    if (res.data.systemName) settings.systemName = res.data.systemName
    if (res.data.siteDescription) settings.siteDescription = res.data.siteDescription
    if (res.data.logoUrl) settings.logoUrl = res.data.logoUrl
    if (res.data.version) settings.version = res.data.version
  } catch {
    // Use defaults
  }
})

async function handleLogin() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await authStore.login({ username: form.username, password: form.password })

        // Remember credentials if checked
        if (form.remember) {
          localStorage.setItem('remembered_username', form.username)
          localStorage.setItem('remember_me', 'true')
        } else {
          localStorage.removeItem('remembered_username')
          localStorage.removeItem('remember_me')
        }

        ElMessage.success('登录成功')
        router.push('/')
      } catch {
        // Error handled by interceptor
      }
    }
  })
}
</script>

<style scoped>
/* ─── CSS Variables (use new design token system) ──── */
.login-page {
  /* Brand accent glow */
  --glow-color: rgba(59, 130, 246, 0.15);

  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-page);
  position: relative;
  overflow: hidden;
  transition: background-color var(--transition-slow);
}

/* ─── Grid background ──────────────────────────────── */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
}

/* ─── Glow orbs (blue accent) ─────────────────────────── */
.bg-glow {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(80px);
}
.bg-glow--1 {
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
  top: -200px; left: -150px;
  animation: glowPulse 8s ease-in-out infinite;
}
.bg-glow--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.06) 0%, transparent 70%);
  bottom: -100px; right: 10%;
  animation: glowPulse 12s ease-in-out infinite reverse;
}
.bg-glow--3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.05) 0%, transparent 70%);
  top: 50%; left: 30%;
  transform: translate(-50%, -50%);
  animation: glowPulse 16s ease-in-out infinite;
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50%       { opacity: 1;   transform: scale(1.08); }
}

/* ─── Wrapper ──────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: stretch;
  width: min(920px, 95vw);
  min-height: 580px;
  border-radius: var(--radius-2xl);
  overflow: hidden;
  box-shadow: var(--shadow-xl), 0 0 0 1px var(--border);
}

/* ─── Brand panel (left) ──────────────────────────── */
.brand-panel {
  flex: 1.05;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #1E3A5F 0%, #0F2440 50%, #081830 100%);
  overflow: hidden;
}

.brand-panel__grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.06) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: radial-gradient(ellipse 80% 80% at 50% 50%, black 40%, transparent 100%);
}

.brand-panel__content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 52px 44px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}

.brand-logo {
  width: 68px; height: 68px;
  background: rgba(59, 130, 246, 0.15);
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(59, 130, 246, 0.3);
  margin-bottom: 28px;
  color: var(--primary);
  transition: transform 0.3s ease;
}
.brand-logo:hover { transform: scale(1.05); }
.brand-logo__img { max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; }
.brand-logo__svg { width: 36px; height: 36px; }

.brand-title {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 10px;
  letter-spacing: 2px;
  text-shadow: 0 2px 12px rgba(59, 130, 246, 0.4);
}

.brand-tagline {
  font-size: 14px;
  color: rgba(59, 130, 246, 0.85);
  margin: 0 0 40px;
  font-weight: 500;
  letter-spacing: 4px;
}

/* Stats decoration */
.brand-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}
.stat-card {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  min-width: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: border-color 0.3s ease;
}
.stat-card:hover { border-color: rgba(59, 130, 246, 0.4); }
.stat-value {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 1px;
}
.stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.45);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.stat-bar {
  width: 100%;
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1px;
  margin-top: 6px;
  overflow: hidden;
}
.stat-bar__fill {
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.6), rgba(59, 130, 246, 1));
  border-radius: 1px;
  transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Corner decorative SVG */
.brand-corner {
  position: absolute;
  bottom: -20px;
  right: -20px;
  width: 200px;
  height: 200px;
  color: rgba(59, 130, 246, 0.4);
  pointer-events: none;
}

/* ─── Login card (right) ───────────────────────────── */
.login-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg);
  position: relative;
}

.login-card__inner {
  width: 100%;
  max-width: 340px;
  padding: 52px 44px;
}

/* Mobile brand */
.mobile-brand {
  display: none;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}
.mobile-brand__img { width: 36px; height: 36px; object-fit: contain; }
.mobile-brand__name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Header */
.login-card__header { margin-bottom: 36px; text-align: center; }
.login-icon {
  width: 44px; height: 44px;
  background: var(--primary-bg);
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
  color: var(--primary);
}
.login-icon svg { width: 22px; height: 22px; }
.login-greeting {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 6px;
}
.login-hint {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

/* Form */
.login-form :deep(.el-form-item) { margin-bottom: 18px; }
.login-form :deep(.el-form-item__label) { display: none; }

.form-input :deep(.el-input__wrapper) {
  background: var(--bg-page) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: none !important;
  padding: 6px 14px !important;
  transition: border-color var(--transition-fast), background var(--transition-slow) !important;
}
.form-input :deep(.el-input__wrapper:hover) {
  border-color: var(--border-hover) !important;
}
.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary) !important;
  background: var(--bg-card) !important;
  box-shadow: 0 0 0 3px var(--primary-bg) !important;
}
.form-input :deep(.el-input__inner) {
  color: var(--text-primary) !important;
  font-size: 14px;
}
.form-input :deep(.el-input__inner::placeholder) { color: var(--text-muted) !important; }
.form-input :deep(.el-input__prefix .el-icon) { color: var(--text-muted) !important; }

/* Remember */
.login-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.remember-check :deep(.el-checkbox__label) {
  color: var(--text-secondary) !important;
  font-size: 13px;
}
.remember-check :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--primary) !important;
  border-color: var(--primary) !important;
}
.remember-check :deep(.el-checkbox__inner) {
  background: var(--bg-hover) !important;
  border-color: var(--border) !important;
}

/* Button */
.login-button {
  width: 100%;
  height: 48px;
  font-size: 15px !important;
  font-weight: 600;
  border-radius: var(--radius-md) !important;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-hover) 100%) !important;
  border: none !important;
  box-shadow: 0 4px 16px var(--primary-shadow) !important;
  transition: box-shadow var(--transition-base), transform var(--transition-fast), filter var(--transition-base) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
  letter-spacing: 2px;
}
.login-button span { letter-spacing: 4px; }
.btn-arrow {
  width: 18px;
  height: 18px;
  transition: transform var(--transition-base);
  flex-shrink: 0;
}
.login-button:hover {
  box-shadow: 0 6px 24px var(--primary-shadow) !important;
  transform: translateY(-2px);
  filter: brightness(1.05);
}
.login-button:hover .btn-arrow { transform: translateX(3px); }
.login-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px var(--primary-shadow) !important;
}

/* Footer */
.login-card__footer {
  text-align: center;
  color: var(--text-muted);
  font-size: 11px;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid var(--border);
  letter-spacing: 0.5px;
}

/* ─── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    min-height: auto;
    width: min(420px, 95vw);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-xl);
  }

  .brand-panel { display: none; }
  .mobile-brand { display: flex; }

  .login-card {
    border-radius: var(--radius-2xl);
    padding: 0;
  }
  .login-card__inner { padding: 40px 36px; }
  .login-greeting { font-size: 22px; }
  .stat-card { min-width: 80px; padding: 10px 12px; }
  .stat-value { font-size: 15px; }
}

@media (max-width: 480px) {
  .login-card__inner { padding: 32px 24px; }
  .login-button { height: 46px; }
}

/* ─── Dark theme override on page level ───────────── */
.login-page[data-theme="dark"],
.login-page:not([data-theme="light"]):not([data-theme="dark"]) {
  background: #09090B;
}
.login-page[data-theme="dark"] .login-card,
.login-page:not([data-theme="light"]):not([data-theme="dark"]) .login-card {
  background: rgba(24, 24, 27, 0.95);
}
.login-page[data-theme="dark"] .brand-panel,
.login-page:not([data-theme="light"]):not([data-theme="dark"]) .brand-panel {
  background: linear-gradient(160deg, #1E3A5F 0%, #0F2440 50%, #081830 100%);
}

/* ─── Light theme ──────────────────────────────────── */
.login-page[data-theme="light"] {
  background: var(--bg-page);
}
.login-page[data-theme="light"] .bg-grid {
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
}
.login-page[data-theme="light"] .brand-panel {
  background: linear-gradient(160deg, #EFF6FF 0%, #DBEAFE 50%, #BFDBFE 100%);
}
.login-page[data-theme="light"] .brand-panel__grid {
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
}
.login-page[data-theme="light"] .brand-title { color: #1E3A5F; text-shadow: none; }
.login-page[data-theme="light"] .brand-tagline { color: rgba(59, 130, 246, 0.85); }
.login-page[data-theme="light"] .stat-card {
  background: rgba(59, 130, 246, 0.08);
  border-color: rgba(59, 130, 246, 0.2);
}
.login-page[data-theme="light"] .stat-value { color: #1E3A5F; }
.login-page[data-theme="light"] .stat-label { color: rgba(0, 0, 0, 0.4); }
.login-page[data-theme="light"] .stat-bar { background: rgba(0, 0, 0, 0.08); }
.login-page[data-theme="light"] .login-icon { background: var(--primary-bg); }
.login-page[data-theme="light"] .login-greeting { color: var(--text-primary); }
.login-page[data-theme="light"] .login-hint { color: var(--text-secondary); }
.mobile-brand__name { color: #1E3A5F; }
.login-page[data-theme="light"] .login-button {
  box-shadow: 0 4px 16px var(--primary-shadow) !important;
}
</style>
