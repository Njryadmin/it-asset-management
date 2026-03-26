import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Asset, AssetForm, Category, Supplier, Department } from '@/types'
import { assetsApi } from '@/api/assets'
import { categoriesApi } from '@/api/categories'
import { suppliersApi } from '@/api/suppliers'
import { departmentsApi } from '@/api/departments'

export const useAssetStore = defineStore('assets', () => {
  const assets = ref<Asset[]>([])
  const total = ref(0)
  const loading = ref(false)
  const categories = ref<Category[]>([])
  const suppliers = ref<Supplier[]>([])
  const departments = ref<Department[]>([])

  const params = ref({
    page: 1,
    page_size: 20,
    keyword: '',
    category_id: undefined as number | undefined,
    status: '',
    department_id: undefined as number | undefined,
    region: ''
  })

  async function fetchAssets() {
    loading.value = true
    try {
      const response = await assetsApi.list(params.value)
      assets.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchOptions() {
    const [catRes, supRes, deptRes] = await Promise.all([
      categoriesApi.getTree(),
      suppliersApi.list({ page_size: 100 }),
      departmentsApi.getTree()
    ])
    categories.value = catRes.data
    suppliers.value = supRes.data.items
    departments.value = deptRes.data
  }

  async function createAsset(data: AssetForm) {
    const response = await assetsApi.create(data)
    return response.data
  }

  async function updateAsset(id: number, data: Partial<AssetForm>) {
    const response = await assetsApi.update(id, data)
    return response.data
  }

  async function deleteAsset(id: number) {
    await assetsApi.delete(id)
  }

  function setParams(newParams: Partial<typeof params.value>) {
    params.value = { ...params.value, ...newParams }
    params.value.page = 1
  }

  function resetParams() {
    params.value = {
      page: 1,
      page_size: 20,
      keyword: '',
      category_id: undefined,
      status: '',
      department_id: undefined,
      region: ''
    }
  }

  return {
    assets,
    total,
    loading,
    categories,
    suppliers,
    departments,
    params,
    fetchAssets,
    fetchOptions,
    createAsset,
    updateAsset,
    deleteAsset,
    setParams,
    resetParams
  }
})
