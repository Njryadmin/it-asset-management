import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, LoginRequest } from '@/types'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)

  async function login(credentials: LoginRequest) {
    loading.value = true
    try {
      const response = await authApi.login(credentials)
      token.value = response.data.access_token
      localStorage.setItem('token', response.data.access_token)
      await fetchUser()
      return true
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await authApi.getMe()
      user.value = response.data
    } catch (error) {
      logout()
      throw error
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  function isLoggedIn() {
    return !!token.value
  }

  // Auto fetch user on init if token exists
  if (token.value) {
    fetchUser().catch(() => {})
  }

  return {
    user,
    token,
    loading,
    login,
    logout,
    fetchUser,
    isLoggedIn
  }
})
