<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

// Apply saved theme on app boot
onMounted(() => {
  const savedTheme = localStorage.getItem('app-theme') || 'default'
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

  const vars = themeVars[savedTheme] || themeVars['default']
  const root = document.documentElement
  for (const [prop, val] of Object.entries(vars)) {
    root.style.setProperty(prop, val)
  }
  // Also set theme-* color aliases for global.css compatibility
  root.style.setProperty('--theme-primary', vars['--el-color-primary'])
  root.style.setProperty('--theme-success', vars['--el-color-success'] || '#67c23a')
  root.style.setProperty('--theme-warning', vars['--el-color-warning'] || '#e6a23c')
  root.style.setProperty('--theme-danger', vars['--el-color-danger'] || '#f56c6c')
  root.style.setProperty('--theme-info', vars['--el-color-info'] || '#909399')
  root.setAttribute('data-theme', savedTheme)
})
</script>
