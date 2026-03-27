<template>
  <div class="login-page">
    <!-- Animated background blobs -->
    <div class="bg-blob bg-blob--1"></div>
    <div class="bg-blob bg-blob--2"></div>
    <div class="bg-blob bg-blob--3"></div>

    <!-- Geometric accent shapes -->
    <div class="geo-shape geo-shape--circle"></div>
    <div class="geo-shape geo-shape--ring"></div>
    <div class="geo-shape geo-shape--dot-grid"></div>

    <div class="login-wrapper">
      <!-- Left brand panel (hidden on mobile) -->
      <div class="brand-panel">
        <div class="brand-panel__content">
          <div class="brand-logo">
            <img v-if="settings.logoUrl" :src="settings.logoUrl" alt="Logo" class="brand-logo__img" />
            <span v-else class="brand-logo__icon">💻</span>
          </div>
          <h2 class="brand-title">{{ settings.systemName || 'IT资产管理系统' }}</h2>
          <p class="brand-desc">{{ settings.siteDescription || '高效、便捷的资产管理解决方案' }}</p>
          <div class="brand-features">
            <div class="feature-item" v-for="f in features" :key="f.icon">
              <span class="feature-icon">{{ f.icon }}</span>
              <span>{{ f.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Login card -->
      <div class="login-card">
        <div class="login-card__inner">
          <!-- Mobile logo -->
          <div class="mobile-brand">
            <img v-if="settings.logoUrl" :src="settings.logoUrl" alt="Logo" class="mobile-brand__img" />
            <span v-else class="mobile-brand__icon">💻</span>
            <span class="mobile-brand__name">{{ settings.systemName || 'IT资产管理系统' }}</span>
          </div>

          <!-- Header -->
          <div class="login-card__header">
            <h1 class="login-greeting">欢迎回来</h1>
            <p class="login-hint">请登录您的账号以继续</p>
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
              <label class="form-label">用户名</label>
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                size="large"
                clearable
                class="form-input"
              />
            </el-form-item>

            <el-form-item prop="password" class="form-item">
              <label class="form-label">密码</label>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
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
              登 录
            </el-button>
          </el-form>

          <!-- Footer -->
          <div class="login-card__footer">
            <span>{{ settings.systemName || 'IT资产管理系统' }} · v1.0</span>
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

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const settings = reactive({
  systemName: 'IT资产管理系统',
  site_title: '',
  siteDescription: '',
  logoUrl: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const features = [
  { icon: '📦', text: '全生命周期资产管理' },
  { icon: '📊', text: '实时数据可视化' },
  { icon: '🔒', text: '细粒度权限控制' }
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

  try {
    const res: any = await settingsApi.get()
    if (res.data.systemName) settings.systemName = res.data.systemName
    if (res.data.siteDescription) settings.siteDescription = res.data.siteDescription
    if (res.data.logoUrl) settings.logoUrl = res.data.logoUrl
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
/* ─── Page layout ─────────────────────────────────── */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0A2E0A;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(26, 173, 25, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(26, 173, 25, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 80%, rgba(26, 173, 25, 0.08) 0%, transparent 50%);
  position: relative;
  overflow: hidden;
}

/* ─── Animated blobs ───────────────────────────────── */
.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}
.bg-blob--1 {
  width: 500px; height: 500px;
  background: rgba(26, 173, 25, 0.12);
  top: -150px; left: -100px;
  animation: blobFloat 12s ease-in-out infinite;
}
.bg-blob--2 {
  width: 400px; height: 400px;
  background: rgba(26, 173, 25, 0.08);
  bottom: -100px; right: -80px;
  animation: blobFloat 16s ease-in-out infinite reverse;
}
.bg-blob--3 {
  width: 300px; height: 300px;
  background: rgba(100, 220, 100, 0.06);
  top: 40%; left: 50%;
  transform: translate(-50%, -50%);
  animation: blobFloat 20s ease-in-out infinite;
}
@keyframes blobFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(30px, -20px) scale(1.05); }
  66%       { transform: translate(-20px, 20px) scale(0.95); }
}

/* ─── Geometric shapes ────────────────────────────── */
.geo-shape { position: absolute; pointer-events: none; }
.geo-shape--circle {
  width: 300px; height: 300px;
  border-radius: 50%;
  border: 1px solid rgba(26, 173, 25, 0.08);
  top: 8%; right: 15%;
  animation: geoRotate 30s linear infinite;
}
.geo-shape--ring {
  width: 180px; height: 180px;
  border-radius: 50%;
  border: 1px solid rgba(26, 173, 25, 0.1);
  bottom: 15%; left: 10%;
  animation: geoRotate 25s linear infinite reverse;
}
.geo-shape--dot-grid {
  width: 200px; height: 200px;
  background-image: radial-gradient(circle, rgba(26, 173, 25, 0.15) 1px, transparent 1px);
  background-size: 20px 20px;
  top: 20%; left: 5%;
  opacity: 0.5;
}
@keyframes geoRotate {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* ─── Wrapper ──────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: stretch;
  width: min(900px, 95vw);
  min-height: 560px;
  gap: 0;
}

/* ─── Brand panel (left) ──────────────────────────── */
.brand-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(26, 173, 25, 0.9) 0%, rgba(15, 130, 15, 0.95) 100%);
  border-radius: 24px 0 0 24px;
  padding: 48px 40px;
  position: relative;
  overflow: hidden;
}
.brand-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 40px,
    rgba(255, 255, 255, 0.015) 40px,
    rgba(255, 255, 255, 0.015) 80px
  );
}
.brand-panel__content {
  position: relative;
  text-align: center;
  color: #fff;
}
.brand-logo {
  width: 72px; height: 72px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 24px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}
.brand-logo__img { width: 100%; height: 100%; object-fit: contain; padding: 8px; }
.brand-logo__icon { font-size: 36px; }
.brand-title {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px;
  letter-spacing: 1px;
}
.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  margin: 0 0 36px;
  line-height: 1.6;
}
.brand-features { display: flex; flex-direction: column; gap: 14px; text-align: left; }
.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}
.feature-icon { font-size: 18px; }

/* ─── Login card (right) ───────────────────────────── */
.login-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 0 24px 24px 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: none;
}
.login-card__inner {
  width: 100%;
  max-width: 340px;
  padding: 48px 40px;
}

/* Mobile brand */
.mobile-brand {
  display: none;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}
.mobile-brand__img { width: 40px; height: 40px; object-fit: contain; }
.mobile-brand__icon { font-size: 28px; }
.mobile-brand__name { font-size: 18px; font-weight: 700; color: #fff; }

/* Header */
.login-card__header { margin-bottom: 32px; }
.login-greeting {
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 6px;
}
.login-hint { font-size: 14px; color: rgba(255, 255, 255, 0.5); margin: 0; }

/* Form */
.login-form :deep(.el-form-item) { margin-bottom: 20px; }
.login-form :deep(.el-form-item__label) { display: none; }

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.form-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 10px !important;
  box-shadow: none !important;
  padding: 4px 12px !important;
  transition: all 0.2s ease !important;
}
.form-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(26, 173, 25, 0.4) !important;
}
.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #1AAD19 !important;
  background: rgba(26, 173, 25, 0.06) !important;
  box-shadow: 0 0 0 3px rgba(26, 173, 25, 0.12) !important;
}
.form-input :deep(.el-input__inner) {
  color: #fff !important;
  font-size: 15px;
}
.form-input :deep(.el-input__inner::placeholder) { color: rgba(255, 255, 255, 0.35) !important; }
.form-input :deep(.el-input__prefix .el-icon) { color: rgba(255, 255, 255, 0.4) !important; }

/* Remember */
.login-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.remember-check :deep(.el-checkbox__label) { color: rgba(255, 255, 255, 0.55) !important; font-size: 13px; }
.remember-check :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #1AAD19 !important;
  border-color: #1AAD19 !important;
}
.remember-check :deep(.el-checkbox__inner) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Button */
.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px !important;
  font-weight: 600;
  border-radius: 10px !important;
  background: linear-gradient(135deg, #1AAD19 0%, #148D14 100%) !important;
  border: none !important;
  box-shadow: 0 4px 20px rgba(26, 173, 25, 0.4) !important;
  transition: all 0.25s ease !important;
  letter-spacing: 4px;
}
.login-button:hover {
  background: linear-gradient(135deg, #17B517 0%, #117A12 100%) !important;
  box-shadow: 0 6px 28px rgba(26, 173, 25, 0.55) !important;
  transform: translateY(-1px);
}
.login-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(26, 173, 25, 0.3) !important;
}

/* Footer */
.login-card__footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.25);
  font-size: 12px;
  padding-top: 28px;
  margin-top: 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* ─── Responsive ───────────────────────────────────── */
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    min-height: auto;
    width: min(420px, 95vw);
  }

  .brand-panel { display: none; }
  .mobile-brand { display: flex; }

  .login-card {
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 40px 32px;
  }

  .login-card__inner { padding: 0; max-width: 100%; }
  .login-greeting { font-size: 22px; }
}

@media (max-width: 480px) {
  .login-card { padding: 32px 24px; }
  .login-button { height: 46px; font-size: 15px !important; }
}
</style>
