<template>
  <div class="asset-form">
    <el-card>
      <template #header>
        <span>{{ isEdit ? '编辑资产' : '新增资产' }}</span>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="form-container"
      >
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入资产名称" />
        </el-form-item>
        <el-form-item label="资产编号" prop="asset_code">
          <el-input v-model="form.asset_code" placeholder="请输入资产编号" />
        </el-form-item>
        <el-form-item label="序列号" prop="serial_number">
          <el-input v-model="form.serial_number" placeholder="请输入序列号" />
        </el-form-item>
        <el-form-item label="资产分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" placeholder="请选择供应商" clearable>
            <el-option v-for="sup in assetStore.suppliers.filter(s => s.isActive)" :key="sup.id" :label="sup.name" :value="sup.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="使用部门" prop="department_id">
          <el-select v-model="form.department_id" placeholder="请选择部门" clearable>
            <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="资产状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="使用中" value="in_use" />
            <el-option label="闲置" value="idle" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="retired" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="购买日期" prop="purchase_date">
          <el-date-picker
            v-model="form.purchase_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="购买价格" prop="purchase_price">
          <el-input-number v-model="form.purchase_price" :min="0" :precision="2" placeholder="请输入购买价格" />
        </el-form-item>
        <el-form-item label="保修到期日" prop="warranty_expire_date">
          <el-date-picker
            v-model="form.warranty_expire_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-input v-model="form.region" placeholder="请输入地区" maxlength="100" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
          <el-button @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { assetsApi } from '@/api/assets'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { AssetStatus } from '@/types'

const router = useRouter()
const route = useRoute()
const assetStore = useAssetStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const assetId = computed(() => Number(route.params.id))
const isEdit = computed(() => !!assetId.value)

const form = reactive({
  name: '',
  asset_code: '',
  serial_number: '',
  category_id: undefined as number | undefined,
  supplier_id: undefined as number | undefined,
  department_id: undefined as number | undefined,
  status: 'idle' as AssetStatus,
  purchase_date: undefined as string | undefined,
  purchase_price: undefined as number | undefined,
  warranty_expire_date: undefined as string | undefined,
  description: '',
  region: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  asset_code: [{ required: true, message: '请输入资产编号', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择资产分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择资产状态', trigger: 'change' }]
}

const flatCategories = computed(() => {
  const result: any[] = []
  function flatten(cats: any[], level = 0) {
    for (const cat of cats) {
      result.push({ ...cat, level })
      if (cat.children?.length) {
        flatten(cat.children, level + 1)
      }
    }
  }
  flatten(assetStore.categories)
  return result
})

const flatDepartments = computed(() => {
  const result: any[] = []
  function flatten(depts: any[], level = 0) {
    for (const dept of depts) {
      result.push({ ...dept, level })
      if (dept.children?.length) {
        flatten(dept.children, level + 1)
      }
    }
  }
  flatten(assetStore.departments)
  return result
})

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isEdit.value) {
          await assetStore.updateAsset(assetId.value, form)
          ElMessage.success('保存成功')
        } else {
          await assetStore.createAsset(form as any)
          ElMessage.success('创建成功')
        }
        router.push('/assets')
      } catch (error) {
        // Error handled by interceptor
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(async () => {
  await assetStore.fetchOptions()
  
  if (isEdit.value) {
    try {
      const response = await assetsApi.get(assetId.value)
      const data = response.data
      Object.assign(form, {
        name: data.name,
        asset_code: data.assetCode,
        serial_number: data.serialNumber,
        category_id: data.categoryId,
        supplier_id: data.supplierId,
        department_id: data.departmentId,
        status: data.status,
        purchase_date: data.purchaseDate,
        purchase_price: data.purchasePrice,
        warranty_expire_date: data.warrantyExpireDate,
        description: data.description,
        region: data.region || ''
      })
    } catch (error) {
      ElMessage.error('加载资产数据失败')
      router.push('/assets')
    }
  }
})
</script>

<style scoped>
.asset-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-container {
  max-width: 600px;
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .asset-form { padding: 14px; }
  .form-container { max-width: 100%; }
}
@media (max-width: 768px) {
  .asset-form { padding: 10px; }
  .form-container { padding: 0; }
  .el-form { }
  .el-form-item { margin-bottom: 16px; }
}
@media (max-width: 480px) {
  .asset-form { padding: 8px; }
  .el-form-item { margin-bottom: 14px; }
}

</style>
