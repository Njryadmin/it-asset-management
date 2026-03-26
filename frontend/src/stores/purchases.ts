import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PurchaseRequest, PurchaseRequestForm, Supplier } from '@/types'
import { purchasesApi } from '@/api/purchases'
import { suppliersApi } from '@/api/suppliers'

export const usePurchaseStore = defineStore('purchases', () => {
  const requests = ref<PurchaseRequest[]>([])
  const pendingRequests = ref<PurchaseRequest[]>([])
  const suppliers = ref<Supplier[]>([])
  const total = ref(0)
  const loading = ref(false)
  const params = ref({
    page: 1,
    page_size: 20,
    keyword: '',
    status: ''
  })

  async function fetchRequests() {
    loading.value = true
    try {
      const response = await purchasesApi.list(params.value)
      requests.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchPending() {
    const response = await purchasesApi.getPending()
    pendingRequests.value = response.data
  }

  async function fetchSuppliers() {
    const response = await suppliersApi.list({ page_size: 100 })
    suppliers.value = response.data.items
  }

  async function create(data: PurchaseRequestForm) {
    const response = await purchasesApi.create(data)
    await fetchRequests()
    return response.data
  }

  async function update(id: number, data: Partial<PurchaseRequestForm>) {
    const response = await purchasesApi.update(id, data)
    await fetchRequests()
    return response.data
  }

  async function submit(id: number) {
    await purchasesApi.submit(id)
    await fetchRequests()
  }

  async function approve(id: number, comment?: string) {
    await purchasesApi.approve(id, comment)
    await fetchRequests()
    await fetchPending()
  }

  async function reject(id: number, comment?: string) {
    await purchasesApi.reject(id, comment)
    await fetchRequests()
    await fetchPending()
  }

  async function markPurchased(id: number, actual_price?: number) {
    await purchasesApi.markPurchased(id, actual_price)
    await fetchRequests()
  }

  async function remove(id: number) {
    await purchasesApi.delete(id)
    await fetchRequests()
  }

  function setParams(newParams: Partial<typeof params.value>) {
    params.value = { ...params.value, ...newParams }
    params.value.page = 1
  }

  return {
    requests,
    pendingRequests,
    suppliers,
    total,
    loading,
    params,
    fetchRequests,
    fetchPending,
    fetchSuppliers,
    create,
    update,
    submit,
    approve,
    reject,
    markPurchased,
    remove,
    setParams
  }
})
