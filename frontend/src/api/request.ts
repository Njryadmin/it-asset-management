import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// Check if value is a plain object (not null, not array, not class instance)
function isPlainObject(obj: any): boolean {
  if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) return false
  return Object.getPrototypeOf(obj) === Object.prototype || Object.getPrototypeOf(obj) === null
}

// snake_case to camelCase
function snakeToCamel(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(item => snakeToCamel(item))
  } else if (isPlainObject(obj)) {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      acc[camelKey] = snakeToCamel(obj[key])
      return acc
    }, {} as any)
  }
  return obj
}

// camelCase to snake_case
function camelToSnake(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(item => camelToSnake(item))
  } else if (isPlainObject(obj)) {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      acc[snakeKey] = camelToSnake(obj[key])
      return acc
    }, {} as any)
  }
  return obj
}

// Response interceptor - convert snake_case to camelCase
request.interceptors.response.use(
  (response) => {
    if (response.data && typeof response.data === 'object') {
      response.data = snakeToCamel(response.data)
    }
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('请求失败，请稍后重试')
    }
    return Promise.reject(error)
  }
)

// Request interceptor - add token and convert camelCase to snake_case
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Convert camelCase to snake_case for request body (skip FormData/URLSearchParams)
    if (config.data && typeof config.data === 'object' && 
        !String(config.headers['Content-Type'] || '').includes('multipart/form-data') && 
        !(config.data instanceof URLSearchParams)) {
      config.data = camelToSnake(config.data)
    }
    
    // Convert params
    if (config.params && typeof config.params === 'object') {
      config.params = camelToSnake(config.params)
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default request

// Helper for file downloads
export function downloadFile(url: string, params?: Record<string, any>, filename?: string) {
  const token = localStorage.getItem('token')
  const queryParams = params ? '?' + new URLSearchParams(
    Object.entries(params).filter(([_, v]) => v !== undefined && v !== null && v !== '').reduce((acc, [k, v]) => {
      acc[k] = String(v)
      return acc
    }, {} as Record<string, string>)
  ).toString() : ''
  
  return fetch(`${request.defaults.baseURL}${url}${queryParams}`, {
    headers: { Authorization: `Bearer ${token}` }
  }).then(response => {
    if (!response.ok) throw new Error('Download failed')
    return response.blob()
  }).then(blob => {
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename || `${url.split('/').pop()}_${Date.now()}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
  }).catch(() => {
    ElMessage.error('下载失败，请稍后重试')
  })
}
