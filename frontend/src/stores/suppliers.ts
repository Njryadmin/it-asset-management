import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Supplier, SupplierForm } from '@/types'
import { suppliersApi } from '@/api/suppliers'

export const useSupplierStore = defineStore('suppliers', () => {
  const suppliers = ref<Supplier[]>([])
  const total = ref(0)
  const loading = ref(false)
  const params = ref({
    page: 1,
    page_size: 20,
    keyword: ''
  })

  async function fetchSuppliers() {
    loading.value = true
    try {
      const response = await suppliersApi.list(params.value)
      suppliers.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function create(data: SupplierForm) {
    const response = await suppliersApi.create(data)
    await fetchSuppliers()
    return response.data
  }

  async function update(id: number, data: Partial<SupplierForm>) {
    const response = await suppliersApi.update(id, data)
    await fetchSuppliers()
    return response.data
  }

  async function remove(id: number) {
    await suppliersApi.delete(id)
    await fetchSuppliers()
  }

  function setParams(newParams: Partial<typeof params.value>) {
    params.value = { ...params.value, ...newParams }
    params.value.page = 1
  }

  return {
    suppliers,
    total,
    loading,
    params,
    fetchSuppliers,
    create,
    update,
    remove,
    setParams
  }
})
