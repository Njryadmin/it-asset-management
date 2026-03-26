import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { usersApi, type UserForm } from '@/api/users'

export const useUserStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const total = ref(0)
  const loading = ref(false)
  const params = ref({
    page: 1,
    page_size: 20,
    keyword: ''
  })

  async function fetchUsers() {
    loading.value = true
    try {
      const response = await usersApi.list(params.value)
      users.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function createUser(data: UserForm) {
    const response = await usersApi.create(data)
    await fetchUsers()
    return response.data
  }

  async function updateUser(id: number, data: Partial<UserForm>) {
    const response = await usersApi.update(id, data)
    await fetchUsers()
    return response.data
  }

  async function deleteUser(id: number) {
    await usersApi.delete(id)
    await fetchUsers()
  }

  return {
    users,
    total,
    loading,
    params,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser
  }
})
