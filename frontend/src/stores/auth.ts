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
      token.value = response.data.accessToken
      localStorage.setItem('token', response.data.accessToken)
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
    } catch (error: any) {
      // Only logout on 401 (invalid token), don't logout on network errors
      if (error.response?.status === 401) {
        logout()
      } else {
        // Network error or server error - just clear user, keep token
        user.value = null
      }
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

  function isAdmin() {
    return user.value?.isSuperuser === true
  }

  return {
    user,
    token,
    loading,
    login,
    logout,
    fetchUser,
    isLoggedIn,
    isAdmin
  }
})
