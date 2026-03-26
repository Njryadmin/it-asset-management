<template>
  <el-container class="layout-container" :class="`theme-${currentTheme}`">

    <!-- Sidebar -->
    <el-aside class="sidebar" :style="sidebarStyle">
      <div class="logo">
        <el-icon :size="22" :style="{ color: sidebarIconColor }">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 7h-4V4c0-1.103-.897-2-2-2h-4c-1.103 0-2 .897-2 2v3H4c-1.103 0-2 .897-2 2v11c0 1.103.897 2 2 2h16c1.103 0 2-.897 2-2V9c0-1.103-.897-2-2-2zM10 4h4v3h-4V4zm10 16H4V9h16v11z"/>
          </svg>
        </el-icon>
        <span class="logo-text">IT资产</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
        :background-color="sidebarMenuBg"
        :text-color="sidebarTextColor"
        :active-text-color="sidebarActiveTextColor"
        :unique-opened="true"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/assets">
          <el-icon><Box /></el-icon>
          <span>资产管理</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Grid /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/departments">
          <el-icon><Office /></el-icon>
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
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main area -->
    <el-container class="main-area">

      <!-- Header -->
      <el-header class="header" :style="headerStyle">
        <div class="header-left">
          <span class="system-name">IT资产管理系统</span>
        </div>
        <div class="header-right">
          <!-- Theme switcher -->
          <div class="theme-switcher">
            <el-tooltip v-for="t in themeOptions" :key="t.key" :content="t.name" placement="bottom">
              <button
                class="theme-dot"
                :class="{ active: currentTheme === t.key }"
                :style="{ background: t.color }"
                @click="switchTheme(t.key)"
              />
            </el-tooltip>
          </div>
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
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const currentTheme = ref('default')

const themeOptions = [
  { key: 'default', name: '默认蓝', color: '#409eff' },
  { key: 'dark',    name: '深色',    color: '#0d1117' },
  { key: 'green',   name: '清新绿',  color: '#2eb872' },
  { key: 'purple',  name: '优雅紫',  color: '#a371f7' },
]

// Theme CSS variable maps
const themeVars: Record<string, Record<string, string>> = {
  default: {
    '--theme-bg':             '#f0f2f5',
    '--theme-sidebar':        '#304156',
    '--theme-sidebar-text':   '#bfcbd9',
    '--theme-sidebar-active': '#263445',
    '--theme-header':         '#ffffff',
    '--theme-card':           '#ffffff',
    '--theme-text-primary':   '#303133',
    '--theme-text-secondary': '#606266',
    '--theme-border':         '#e4e7ed',
    '--theme-border-light':   '#f0f2f5',
    '--theme-shadow':         '0 2px 12px rgba(0,0,0,0.08)',
    '--theme-shadow-hover':   '0 4px 20px rgba(0,0,0,0.12)',
    '--el-color-primary':     '#409eff',
  },
  dark: {
    '--theme-bg':             '#0d1117',
    '--theme-sidebar':        '#161b22',
    '--theme-sidebar-text':   '#8b949e',
    '--theme-sidebar-active': 'rgba(31,111,235,0.2)',
    '--theme-header':         '#161b22',
    '--theme-card':           '#161b22',
    '--theme-text-primary':   '#c9d1d9',
    '--theme-text-secondary': '#8b949e',
    '--theme-border':          '#30363d',
    '--theme-border-light':   '#21262d',
    '--theme-shadow':         '0 2px 12px rgba(0,0,0,0.4)',
    '--theme-shadow-hover':   '0 4px 20px rgba(0,0,0,0.5)',
    '--el-color-primary':     '#409eff',
  },
  green: {
    '--theme-bg':             '#f0f9eb',
    '--theme-sidebar':        '#1a5c1a',
    '--theme-sidebar-text':   '#a6e7b0',
    '--theme-sidebar-active': 'rgba(46,184,114,0.13)',
    '--theme-header':         '#ffffff',
    '--theme-card':           '#ffffff',
    '--theme-text-primary':   '#303133',
    '--theme-text-secondary': '#606266',
    '--theme-border':         '#e1f3d8',
    '--theme-border-light':   '#f0f9eb',
    '--theme-shadow':         '0 2px 12px rgba(46,184,114,0.12)',
    '--theme-shadow-hover':   '0 4px 20px rgba(46,184,114,0.2)',
    '--el-color-primary':     '#2eb872',
  },
  purple: {
    '--theme-bg':             '#f5f3ff',
    '--theme-sidebar':        '#2d1b4e',
    '--theme-sidebar-text':   '#d2b4fa',
    '--theme-sidebar-active': 'rgba(163,113,247,0.13)',
    '--theme-header':         '#ffffff',
    '--theme-card':           '#ffffff',
    '--theme-text-primary':   '#303133',
    '--theme-text-secondary': '#606266',
    '--theme-border':         '#ede9fe',
    '--theme-border-light':   '#f5f3ff',
    '--theme-shadow':         '0 2px 12px rgba(163,113,247,0.12)',
    '--theme-shadow-hover':   '0 4px 20px rgba(163,113,247,0.2)',
    '--el-color-primary':     '#a371f7',
  },
}

const sidebarStyle = computed(() => ({
  backgroundColor: themeVars[currentTheme.value]?.['--theme-sidebar'] || '#304156',
}))

const headerStyle = computed(() => ({
  backgroundColor: themeVars[currentTheme.value]?.['--theme-header'] || '#ffffff',
  boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
}))

const sidebarMenuBg = computed(() => themeVars[currentTheme.value]?.['--theme-sidebar'] || '#304156')
const sidebarTextColor = computed(() => themeVars[currentTheme.value]?.['--theme-sidebar-text'] || '#bfcbd9')
const sidebarActiveTextColor = computed(() => {
  const map: Record<string, string> = {
    default: '#409eff',
    dark: '#409eff',
    green: '#2eb872',
    purple: '#a371f7',
  }
  return map[currentTheme.value] || '#409eff'
})
const sidebarIconColor = computed(() => sidebarTextColor.value)

function switchTheme(key: string) {
  currentTheme.value = key
  localStorage.setItem('app-theme', key)
  applyThemeVars(key)
  // Update Element Plus primary color
  document.documentElement.style.setProperty(
    '--el-color-primary',
    themeVars[key]?.['--el-color-primary'] || '#409eff'
  )
}

function applyThemeVars(key: string) {
  const vars = themeVars[key]
  if (!vars) return
  const root = document.documentElement
  for (const [prop, val] of Object.entries(vars)) {
    root.style.setProperty(prop, val)
  }
  root.setAttribute('data-theme', key)
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

onMounted(() => {
  const saved = localStorage.getItem('app-theme')
  if (saved && themeVars[saved]) {
    currentTheme.value = saved
  }
  applyThemeVars(currentTheme.value)
})

watch(currentTheme, (val) => {
  applyThemeVars(val)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px !important;
  min-width: 220px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: width var(--transition-normal), background-color var(--transition-normal);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 12px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
}

.sidebar-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 2px 8px;
  border-radius: 8px;
  padding-left: 16px !important;
  font-size: 14px;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.sidebar-menu .el-menu-item:hover {
  background: var(--theme-sidebar-active) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: var(--theme-sidebar-active) !important;
  color: v-bind(sidebarActiveTextColor) !important;
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 16px;
}

/* ── Header ── */
.header {
  height: 60px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px !important;
  z-index: 10;
  flex-shrink: 0;
}

.system-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--theme-text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Theme switcher */
.theme-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  background: var(--theme-border-light);
  border-radius: 20px;
}

.theme-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.theme-dot:hover {
  transform: scale(1.2);
}

.theme-dot.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px currentColor;
  transform: scale(1.1);
}

/* User info */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: background-color var(--transition-fast);
}

.user-info:hover {
  background: var(--theme-border-light);
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--el-color-primary, #409eff);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--theme-text-primary);
}

.chevron {
  color: var(--theme-text-secondary);
  font-size: 12px;
}

/* ── Main content ── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  background: var(--theme-bg);
  padding: 20px;
  transition: background-color var(--transition-normal);
}

/* ── Fade transition ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
