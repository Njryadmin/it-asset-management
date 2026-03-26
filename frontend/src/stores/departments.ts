import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Department, DepartmentForm } from '@/types'
import { departmentsApi } from '@/api/departments'

export const useDepartmentStore = defineStore('departments', () => {
  const departments = ref<Department[]>([])
  const loading = ref(false)

  async function fetchTree() {
    loading.value = true
    try {
      const response = await departmentsApi.getTree()
      departments.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function create(data: DepartmentForm) {
    const response = await departmentsApi.create(data)
    await fetchTree()
    return response.data
  }

  async function update(id: number, data: Partial<DepartmentForm>) {
    const response = await departmentsApi.update(id, data)
    await fetchTree()
    return response.data
  }

  async function remove(id: number) {
    await departmentsApi.delete(id)
    await fetchTree()
  }

  return {
    departments,
    loading,
    fetchTree,
    create,
    update,
    remove
  }
})
