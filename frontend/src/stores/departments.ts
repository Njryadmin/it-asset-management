import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Department } from '@/types'
import { departmentsApi, type DepartmentForm } from '@/api/departments'

export const useDepartmentStore = defineStore('departments', () => {
  const departments = ref<Department[]>([])
  const tree = ref<Department[]>([])
  const total = ref(0)
  const loading = ref(false)
  const params = ref({
    page: 1,
    page_size: 20,
    keyword: ''
  })

  async function fetchDepartments() {
    loading.value = true
    try {
      const response = await departmentsApi.list(params.value)
      departments.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchTree() {
    const response = await departmentsApi.getTree()
    tree.value = response.data
  }

  async function createDepartment(data: DepartmentForm) {
    const response = await departmentsApi.create(data)
    await fetchDepartments()
    await fetchTree()
    return response.data
  }

  async function updateDepartment(id: number, data: Partial<DepartmentForm>) {
    const response = await departmentsApi.update(id, data)
    await fetchDepartments()
    await fetchTree()
    return response.data
  }

  async function deleteDepartment(id: number) {
    await departmentsApi.delete(id)
    await fetchDepartments()
    await fetchTree()
  }

  return {
    departments,
    tree,
    total,
    loading,
    params,
    fetchDepartments,
    fetchTree,
    createDepartment,
    updateDepartment,
    deleteDepartment
  }
})
