<template>
  <el-container class="layout-container">

    <!-- Mobile Overlay -->
    <div
      v-if="sidebarVisible"
      class="sidebar-overlay"
      @click="sidebarVisible = false"
    />

    <!-- Sidebar -->
    <el-aside
      class="sidebar"
      :class="{ 'sidebar--open': sidebarVisible }"
    >
      <div class="sidebar__header">
        <div class="sidebar__logo" @click="$router.push('/')">
          <img v-if="siteLogo" :src="siteLogo" class="sidebar__logo-img" alt="logo" />
          <span v-else class="sidebar__logo-icon">💻</span>
        </div>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        class="sidebar__menu"
        :collapse="false"
        :unique-opened="true"
        @select="onMenuSelect"
      >
        <!-- 仪表盘 -->
        <el-menu-item index="/">
          <el-icon aria-hidden="true"><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <!-- 资产管理（折叠） -->
        <el-sub-menu index="/assets">
          <template #title>
            <el-icon aria-hidden="true"><Box /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/assets">
            <el-icon aria-hidden="true"><Box /></el-icon>
            <span>资产列表</span>
          </el-menu-item>
          <el-menu-item index="/assets/create">
            <el-icon aria-hidden="true"><Plus /></el-icon>
            <span>新增资产</span>
          </el-menu-item>
          <el-menu-item index="/asset-transfers">
            <el-icon aria-hidden="true"><RefreshRight /></el-icon>
            <span>资产转移</span>
          </el-menu-item>
          <el-menu-item index="/depreciation">
            <el-icon aria-hidden="true"><Wallet /></el-icon>
            <span>折旧报表</span>
          </el-menu-item>
          <el-divider style="margin: 8px 0" />
          <el-menu-item index="/categories">
            <el-icon aria-hidden="true"><Grid /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/departments">
            <el-icon aria-hidden="true"><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
          <el-menu-item index="/suppliers">
            <el-icon aria-hidden="true"><Shop /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 采购管理 -->
        <el-menu-item index="/purchases">
          <el-icon aria-hidden="true"><ShoppingCart /></el-icon>
          <span>采购申请</span>
        </el-menu-item>

        <!-- 用户管理 [admin] -->
        <el-menu-item v-if="authStore.user?.isSuperuser" index="/users">
          <el-icon aria-hidden="true"><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>

        <!-- 审批管理 [admin]（折叠） -->
        <el-sub-menu v-if="authStore.user?.isSuperuser" index="/approvals-group">
          <template #title>
            <el-icon aria-hidden="true"><DocumentChecked /></el-icon>
            <span>审批管理</span>
          </template>
          <el-menu-item index="/approvals">
            <el-icon aria-hidden="true"><Clock /></el-icon>
            <span>待我审批</span>
          </el-menu-item>
          <el-menu-item index="/approval-flows">
            <el-icon aria-hidden="true"><Setting /></el-icon>
            <span>流程配置</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 审计日志 [admin] -->
        <el-menu-item v-if="authStore.user?.isSuperuser" index="/audit">
          <el-icon aria-hidden="true"><Histogram /></el-icon>
          <span>审计日志</span>
        </el-menu-item>

        <!-- 报表中心 [admin]（折叠） -->
        <el-sub-menu v-if="authStore.user?.isSuperuser" index="/reports-group">
          <template #title>
            <el-icon aria-hidden="true"><DataAnalysis /></el-icon>
            <span>报表中心</span>
          </template>
          <el-menu-item index="/reports">
            <el-icon aria-hidden="true"><PieChart /></el-icon>
            <span>资产总览</span>
          </el-menu-item>
          <el-menu-item index="/reports?tab=category">
            <el-icon aria-hidden="true"><Grid /></el-icon>
            <span>分类分布</span>
          </el-menu-item>
          <el-menu-item index="/reports?tab=department">
            <el-icon aria-hidden="true"><OfficeBuilding /></el-icon>
            <span>部门分布</span>
          </el-menu-item>
          <el-menu-item index="/reports?tab=importance">
            <el-icon aria-hidden="true"><TrendCharts /></el-icon>
            <span>重要度分析</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 系统设置 -->
        <el-menu-item index="/settings">
          <el-icon aria-hidden="true"><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar__footer">
        <div class="sidebar__version">{{ appVersion }}</div>
      </div>
    </el-aside>

    <!-- Main Area -->
    <el-container class="main-area">

      <!-- Breadcrumb -->
      <div class="breadcrumb-bar" v-if="$route.path !== '/'">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path.startsWith('/assets')">资产管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/assets' || $route.path === '/assets/create'">{{ $route.path === '/assets/create' ? '新增资产' : '资产列表' }}</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/categories'">分类管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/departments'">部门管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/suppliers'">供应商管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/purchases'">采购申请</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/users'">用户管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/approvals' || $route.path === '/approvals-group'">审批管理</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/approval-flows'">流程配置</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/reports' || $route.path.startsWith('/reports/')">报表中心</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/depreciation'">折旧报表</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/asset-transfers'">资产转移</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/maintenance'">维保记录</el-breadcrumb-item>
          <el-breadcrumb-item v-if="$route.path === '/settings'">系统设置</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <!-- Header -->
      <el-header class="header">
        <!-- Hamburger (mobile only) -->
        <button
          class="hamburger"
          :class="{ 'hamburger--active': sidebarVisible }"
          @click="sidebarVisible = !sidebarVisible"
          aria-label="切换菜单"
        >
          <span /><span /><span />
        </button>

        <!-- Page title -->
        <div class="header__title">
          {{ pageTitle }}
        </div>

        <div class="header__right">
          <!-- Theme Toggle (Lobe Theme style) -->
          <button class="theme-toggle" @click="toggleTheme" :title="currentTheme === 'dark' ? '切换浅色主题' : '切换深色主题'">
            <el-icon :size="18">
              <Sunny v-if="currentTheme === 'dark'" />
              <Moon v-else />
            </el-icon>
          </button>

          <!-- User dropdown -->
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <div class="user-avatar">
                <el-icon><User /></el-icon>
              </div>
              <span class="user-name">{{ authStore.user?.fullName || authStore.user?.username }}</span>
              <el-icon class="chevron"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>

    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { settingsApi } from '@/api/settings'
import { ElMessageBox } from 'element-plus'
import { Sunny, Moon, DocumentChecked, Histogram, DataAnalysis, RefreshRight, Wallet, Plus, PieChart, TrendCharts, Grid, OfficeBuilding, Clock, Setting } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const sidebarVisible = ref(false)
const siteLogo = ref('')
const siteName = ref('')
const appVersion = ref('v2.0.0')
const currentTheme = ref((window as any).__getTheme?.() || 'default')

function toggleTheme() {
  ;(window as any).__toggleTheme?.()
  currentTheme.value = (window as any).__getTheme?.() || 'default'
}

const routeTitleMap: Record<string, string> = {
  '/': '仪表盘',
  '/assets': '资产列表',
  '/categories': '分类管理',
  '/departments': '部门管理',
  '/suppliers': '供应商管理',
  '/purchases': '采购管理',
  '/users': '用户管理',
  '/approvals': '审批管理',
  '/audit': '审计日志',
  '/asset-transfers': '资产转移记录',
  '/reports': '报表中心',
  '/depreciation': '折旧报表',
  '/settings': '系统设置',
}

const pageTitle = computed(() => {
  return routeTitleMap[route.path] || 'IT资产管理系统'
})

function onMenuSelect() {
  // Close sidebar on mobile after selecting a menu item
  if (window.innerWidth < 768) {
    sidebarVisible.value = false
    document.body.style.overflow = ''
  }
}

function handleCommand(command: string) {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      authStore.logout()
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'settings') {
    router.push('/settings')
  }
}

// Close sidebar on window resize to desktop
watch(() => window.innerWidth, (w) => {
  if (w >= 768) {
    sidebarVisible.value = false
    document.body.style.overflow = ''
  }
})

// Prevent body scroll when mobile sidebar is open
watch(sidebarVisible, (visible) => {
  if (window.innerWidth < 768) {
    document.body.style.overflow = visible ? 'hidden' : ''
  }
})

// Fetch user and settings on mount
onMounted(async () => {
  if (authStore.token) {
    authStore.fetchUser().catch(() => {})
  }
  // Fetch site settings for logo/name
  try {
    const res = await settingsApi.get()
    siteLogo.value = (res.data as any).logoUrl || ''
    siteName.value = (res.data as any).systemName || 'IT资产'
    appVersion.value = (res.data as any).version || 'v2.0.0'
  } catch {
    // ignore
  }
})
</script>

<style scoped>
/* ── Layout ── */
.layout-container {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px !important;
  min-width: 220px;
  background-color: var(--sidebar-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition-normal), background-color var(--transition-slow);
  z-index: 100;
  flex-shrink: 0;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.06);
  border-right: 1px solid var(--sidebar-border);
}

.sidebar__header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.sidebar__logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  width: 100%;
  padding: 0;
}

.sidebar__logo-img {
  width: 100%;
  height: 44px;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.sidebar__logo-icon {
  font-size: 20px;
}

.sidebar__logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--sidebar-text);
  letter-spacing: 1px;
}

/* ── Menu ── */
.sidebar__menu {
  flex: 1;
  border-right: none !important;
  background-color: transparent !important;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 6px 0;
}

.sidebar__menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 2px 10px;
  border-radius: var(--radius-md);
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
  color: var(--sidebar-text) !important;
  background-color: transparent !important;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar__menu :deep(.el-menu-item:hover) {
  background-color: var(--sidebar-bg-hover) !important;
  color: var(--sidebar-text-active) !important;
}

.sidebar__menu :deep(.el-menu-item.is-active) {
  background-color: var(--sidebar-bg-active) !important;
  color: var(--sidebar-text-active) !important;
}

.sidebar__menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--sidebar-icon-active) !important;
}

.sidebar__menu :deep(.el-menu-item .el-icon) {
  font-size: 17px;
  color: var(--sidebar-icon);
  flex-shrink: 0;
}

.sidebar__menu :deep(.el-menu-item span) {
  font-weight: 500;
}

/* Sub-menu (资产管理) */
.sidebar__menu :deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  margin: 2px 10px;
  border-radius: var(--radius-md);
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
  color: var(--sidebar-text) !important;
  background-color: transparent !important;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar__menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--sidebar-bg-hover) !important;
  color: var(--sidebar-text-active) !important;
}

.sidebar__menu :deep(.el-sub-menu__title .el-icon) {
  font-size: 17px;
  color: var(--sidebar-icon);
  flex-shrink: 0;
}

.sidebar__menu :deep(.el-sub-menu__title span) {
  font-weight: 500;
}

.sidebar__menu :deep(.el-sub-menu .el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 1px 10px 1px 16px;
  padding-left: 44px !important;
  padding-right: 16px !important;
  font-size: 13px;
  min-width: 0;
}

.sidebar__menu :deep(.el-sub-menu .el-menu-item .el-icon) {
  font-size: 16px;
}

/* Sub-menu item active state */
.sidebar__menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background-color: var(--sidebar-bg-active) !important;
  color: var(--sidebar-text-active) !important;
  border-radius: var(--radius-md);
}

.sidebar__menu :deep(.el-sub-menu .el-menu-item.is-active .el-icon) {
  color: var(--sidebar-icon-active) !important;
}

/* Sub-menu opened state - parent title icon */
.sidebar__menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title .el-icon) {
  color: var(--sidebar-icon-active) !important;
}

.sidebar__footer {
  padding: 12px 20px;
  border-top: 1px solid var(--sidebar-border);
  flex-shrink: 0;
}

.sidebar__version {
  font-size: 11px;
  color: var(--text-muted);
  text-align: center;
}

/* ── Overlay (mobile) ── */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: var(--overlay-bg);
  backdrop-filter: var(--overlay-blur);
  z-index: 99;
}

/* ── Breadcrumb ── */
.breadcrumb-bar {
  padding: 8px 20px;
  background: var(--bg-page);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

/* ── Header ── */
.header {
  height: var(--header-height) !important;
  display: flex;
  align-items: center;
  padding: 0 20px !important;
  background-color: var(--header-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--header-border);
  box-shadow: var(--header-shadow);
  z-index: 10;
  flex-shrink: 0;
  gap: 12px;
  transition: background-color var(--transition-slow), border-color var(--transition-base);
  overflow: hidden;
}

.header__title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--header-text);
}

.header__right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  overflow: hidden;
}

/* ── Theme Toggle Button ── */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--bg-hover);
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--text-secondary);
  transition: background-color var(--transition-fast), color var(--transition-fast), box-shadow var(--transition-fast), transform var(--transition-fast);
  flex-shrink: 0;
}
.theme-toggle:hover {
  background: var(--bg-active);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
  transform: scale(1.05);
}
.theme-toggle:active {
  transform: scale(0.94);
}

/* ── Hamburger ── */
.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 36px;
  height: 36px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}
.hamburger:hover {
  background-color: var(--bg-hover);
}
.hamburger span {
  display: block;
  height: 2px;
  background-color: var(--header-text);
  border-radius: 1px;
  transition: all var(--transition-fast);
}
.hamburger--active span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}
.hamburger--active span:nth-child(2) {
  opacity: 0;
}
.hamburger--active span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* ── User Info ── */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
  max-width: 180px;
  overflow: hidden;
}
.user-info:hover {
  background-color: var(--bg-hover);
}
.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  flex-shrink: 0;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--header-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
  max-width: 100px;
}
.chevron {
  color: var(--header-text-secondary);
  font-size: 12px;
}

/* ── Main Content ── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-page);
  padding: var(--space-4);
  transition: background-color var(--transition-slow);
}

/* ── Fade Transition ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity var(--transition-base);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* ── Responsive: Mobile ── */
@media (max-width: 768px) {
  .hamburger {
    display: flex;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 220px !important;
    min-width: 220px;
    transform: translateX(-100%);
    z-index: var(--z-fixed);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
  }

  .sidebar--open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: block;
  }

  .user-name {
    display: none;
  }

  .header {
    padding: 0 16px !important;
  }

  .main-content {
    padding: var(--space-3);
  }
}
</style>
