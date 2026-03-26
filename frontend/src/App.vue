<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

// Local theme definitions — must match Settings.vue's localThemes
const localThemes: Record<string, any> = {
  default: {
    name: '默认主题',
    primary: '#1AAD19',
    success: '#07C160',
    warning: '#FF991A',
    danger: '#FA5151',
    info: '#909399',
    bg_color: '#F5F5F5',
    bg_color_secondary: '#E8E8E8',
    sidebar_color: 'rgba(255, 255, 255, 0.9)',
    sidebar_text: '#333333',
    sidebar_active: 'rgba(26, 173, 25, 0.12)',
    header_color: '#ffffff',
    card_bg: '#ffffff',
    text_primary: '#333333',
    text_secondary: '#666666',
    text_placeholder: '#999999',
    border_color: '#E5E5E5',
    border_light: '#F0F0F0',
    shadow: '0 2px 12px rgba(0,0,0,0.06)',
    shadow_hover: '0 4px 16px rgba(0,0,0,0.1)'
  },
  dark: {
    name: '深色主题',
    primary: '#07C160',
    success: '#07C160',
    warning: '#FF991A',
    danger: '#FA5151',
    info: '#909399',
    bg_color: '#1F1F1F',
    bg_color_secondary: '#2D2D2D',
    sidebar_color: '#191919',
    sidebar_text: '#E0E0E0',
    sidebar_active: 'rgba(7,193,96,0.15)',
    header_color: '#1F1F1F',
    card_bg: '#252525',
    text_primary: '#FFFFFF',
    text_secondary: '#A0A0A0',
    text_placeholder: '#6B6B6B',
    border_color: '#3A3A3C',
    border_light: '#2D2D2D',
    shadow: '0 2px 8px rgba(0,0,0,0.3)',
    shadow_hover: '0 4px 16px rgba(0,0,0,0.4)'
  }
}

function applyTheme(key: string) {
  const theme = localThemes[key]
  if (!theme) return
  const root = document.documentElement
  // Apply wechat-* CSS variables that global.css expects
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
  root.style.setProperty('--wechat-sidebar-active-bg', theme.sidebar_active)
  root.style.setProperty('--wechat-shadow', theme.shadow)
  root.style.setProperty('--wechat-shadow-hover', theme.shadow_hover)
  // Element Plus overrides
  root.style.setProperty('--el-color-primary', theme.primary)
  root.style.setProperty('--el-bg-color', theme.bg_color)
  root.style.setProperty('--el-bg-color-page', theme.bg_color)
  root.style.setProperty('--el-bg-color-overlay', theme.card_bg)
  root.style.setProperty('--el-text-color-primary', theme.text_primary)
  root.style.setProperty('--el-text-color-regular', theme.text_secondary)
  root.style.setProperty('--el-border-color', theme.border_color)
  root.style.setProperty('--el-fill-color-blank', theme.card_bg)
  // Directly set body background to ensure it applies immediately
  document.body.style.backgroundColor = theme.bg_color
}

onMounted(() => {
  // Restore theme from localStorage on app start
  const savedTheme = localStorage.getItem('app-theme')
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
    applyTheme(savedTheme)
  }
})
</script>
