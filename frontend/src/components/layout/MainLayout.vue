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
        <div class="sidebar__logo">
          <span class="sidebar__logo-icon">💻</span>
          <span class="sidebar__logo-text">IT资产</span>
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
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-sub-menu index="/assets">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/assets">
            <el-icon><Box /></el-icon>
            <span>资产列表</span>
          </el-menu-item>
          <el-menu-item index="/categories">
            <el-icon><Grid /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/departments">
          <el-icon><OfficeBuilding /></el-icon>
          <span>部门管理</span>
        </el-menu-item>
        <el-menu-item index="/suppliers">
          <el-icon><Shop /></el-icon>
          <span>供应商</span>
        </el-menu-item>
        <el-menu-item index="/purchases">
          <el-icon><ShoppingCart /></el-icon>
          <span>采购管理</span>
        </el-menu-item>
        <el-menu-item v-if="authStore.user?.isSuperuser" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar__footer">
        <div class="sidebar__version">v1.0.0</div>
      </div>
    </el-aside>

    <!-- Main Area -->
    <el-container class="main-area">

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
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const sidebarVisible = ref(false)

const routeTitleMap: Record<string, string> = {
  '/': '仪表盘',
  '/assets': '资产列表',
  '/categories': '分类管理',
  '/departments': '部门管理',
  '/suppliers': '供应商管理',
  '/purchases': '采购管理',
  '/users': '用户管理',
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

// Fetch user on mount if token exists
onMounted(() => {
  if (authStore.token) {
    authStore.fetchUser().catch(() => {})
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
  width: 210px !important;
  min-width: 210px;
  background-color: var(--wechat-sidebar);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform var(--transition-normal);
  z-index: 100;
  flex-shrink: 0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.06);
}

.sidebar__header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.sidebar__logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar__logo-icon {
  font-size: 20px;
}

.sidebar__logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--wechat-sidebar-text);
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
  border-radius: var(--radius-sm);
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
  color: var(--wechat-sidebar-text) !important;
  background-color: transparent !important;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar__menu :deep(.el-menu-item:hover) {
  background-color: var(--wechat-sidebar-hover-bg) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.sidebar__menu :deep(.el-menu-item.is-active) {
  background-color: var(--wechat-sidebar-active-bg) !important;
  color: #fff !important;
}

.sidebar__menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--wechat-primary) !important;
}

.sidebar__menu :deep(.el-menu-item .el-icon) {
  font-size: 17px;
  color: var(--wechat-sidebar-icon);
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
  border-radius: var(--radius-sm);
  padding-left: 16px !important;
  padding-right: 16px !important;
  font-size: 14px;
  color: var(--wechat-sidebar-text) !important;
  background-color: transparent !important;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar__menu :deep(.el-sub-menu__title:hover) {
  background-color: var(--wechat-sidebar-hover-bg) !important;
  color: rgba(255, 255, 255, 0.9) !important;
}

.sidebar__menu :deep(.el-sub-menu__title .el-icon) {
  font-size: 17px;
  color: var(--wechat-sidebar-icon);
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

.sidebar__footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.sidebar__version {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.25);
  text-align: center;
}

/* ── Overlay (mobile) ── */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  backdrop-filter: blur(2px);
}

/* ── Header ── */
.header {
  height: 56px !important;
  display: flex;
  align-items: center;
  padding: 0 20px !important;
  background-color: var(--wechat-card);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  z-index: 10;
  flex-shrink: 0;
  gap: 12px;
}

.header__title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--wechat-text);
}

.header__right {
  display: flex;
  align-items: center;
  gap: 12px;
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
  background-color: var(--wechat-bg);
}
.hamburger span {
  display: block;
  height: 2px;
  background-color: var(--wechat-text);
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
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}
.user-info:hover {
  background-color: var(--wechat-bg);
}
.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--wechat-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--wechat-text);
}
.chevron {
  color: var(--wechat-text-secondary);
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
  background: var(--wechat-bg);
  padding: 16px;
  transition: background-color var(--transition-normal);
}

/* ── Fade Transition ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
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
    width: 210px !important;
    min-width: 210px;
    transform: translateX(-100%);
    z-index: 200;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
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
    padding: 12px;
  }
}
</style>
