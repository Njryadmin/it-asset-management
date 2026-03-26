import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category, CategoryForm } from '@/types'
import { categoriesApi } from '@/api/categories'

export const useCategoryStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchTree() {
    loading.value = true
    try {
      const response = await categoriesApi.getTree()
      categories.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function create(data: CategoryForm) {
    const response = await categoriesApi.create(data)
    await fetchTree()
    return response.data
  }

  async function update(id: number, data: Partial<CategoryForm>) {
    const response = await categoriesApi.update(id, data)
    await fetchTree()
    return response.data
  }

  async function remove(id: number) {
    await categoriesApi.delete(id)
    await fetchTree()
  }

  return {
    categories,
    loading,
    fetchTree,
    create,
    update,
    remove
  }
})
