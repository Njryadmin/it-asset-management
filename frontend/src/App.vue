<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

// Local theme definitions — must match Settings.vue's localThemes
const localThemes: Record<string, any> = {
  default: {
    name: '默认主题',
    primary: '#3B82F6',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#6366F1',
    bg_color: '#F1F5F9',
    bg_color_secondary: '#E8EDF3',
    sidebar_color: 'rgba(255, 255, 255, 0.9)',
    sidebar_text: '#475569',
    sidebar_active_bg: 'rgba(59, 130, 246, 0.1)',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#0F172A',
    text_secondary: '#475569',
    text_placeholder: '#94A3B8',
    border_color: '#E2E8F0',
    border_light: '#F1F5F9',
    shadow: '0 1px 3px rgba(0,0,0,0.06)',
    shadow_hover: '0 4px 6px rgba(0,0,0,0.07)'
  },
  dark: {
    name: '深色主题',
    primary: '#3B82F6',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#6366F1',
    bg_color: '#09090B',
    bg_color_secondary: '#111113',
    sidebar_color: 'rgba(16, 16, 18, 0.92)',
    sidebar_text: '#A1A1AA',
    sidebar_active_bg: 'rgba(59, 130, 246, 0.12)',
    header_color: 'rgba(16, 16, 18, 0.88)',
    card_bg: 'rgba(24, 24, 27, 0.85)',
    text_primary: '#FAFAFA',
    text_secondary: '#A1A1AA',
    text_placeholder: '#71717A',
    border_color: 'rgba(255, 255, 255, 0.08)',
    border_light: 'rgba(255, 255, 255, 0.05)',
    shadow: '0 4px 16px rgba(0,0,0,0.4)',
    shadow_hover: '0 8px 24px rgba(0,0,0,0.5)'
  }
}

function applyTheme(key: string) {
  const theme = localThemes[key]
  if (!theme) return
  const root = document.documentElement

  // Apply legacy wechat-* CSS variables (backward compat)
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
  root.style.setProperty('--wechat-shadow', theme.shadow)
  root.style.setProperty('--wechat-shadow-hover', theme.shadow_hover)

  // Apply Element Plus overrides
  root.style.setProperty('--el-color-primary', theme.primary)
  root.style.setProperty('--el-bg-color', theme.bg_color)
  root.style.setProperty('--el-bg-color-page', theme.bg_color)
  root.style.setProperty('--el-bg-color-overlay', theme.card_bg)
  root.style.setProperty('--el-text-color-primary', theme.text_primary)
  root.style.setProperty('--el-text-color-regular', theme.text_secondary)
  root.style.setProperty('--el-border-color', theme.border_color)
  root.style.setProperty('--el-fill-color-blank', theme.card_bg)

  // Legacy aliases
  root.style.setProperty('--theme-primary', theme.primary)
  root.style.setProperty('--theme-bg', theme.bg_color)
  root.style.setProperty('--theme-card', theme.card_bg)

  // Update .dark class for new theme system
  if (key === 'dark') {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }

  // Directly set body background
  document.body.style.backgroundColor = theme.bg_color
}

onMounted(() => {
  // Restore theme from localStorage on app start
  const savedTheme = localStorage.getItem('app-theme') || 'default'
  document.documentElement.setAttribute('data-theme', savedTheme)

  // Apply .dark class for new theme system
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }

  applyTheme(savedTheme)

  // Expose global theme toggle for header button
  ;(window as any).__toggleTheme = () => {
    const current = localStorage.getItem('app-theme') || 'default'
    const next = current === 'default' ? 'dark' : 'default'
    localStorage.setItem('app-theme', next)
    document.documentElement.setAttribute('data-theme', next)

    // New class-based toggle
    if (next === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    applyTheme(next)
  }

  ;(window as any).__getTheme = () => localStorage.getItem('app-theme') || 'default'
  ;(window as any).__isDark = () => localStorage.getItem('app-theme') === 'dark'
})
</script>
