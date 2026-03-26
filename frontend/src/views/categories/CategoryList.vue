<template>
  <div class="category-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            新增分类
          </el-button>
        </div>
      </template>

      <el-tree
        :data="categoryStore.categories"
        :props="{ label: 'name', children: 'children' }"
        default-expand-all
        class="category-tree"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span>{{ data.name }}</span>
            <span class="node-actions">
              <el-button type="primary" link size="small" @click="showDialog('create', data)">添加子分类</el-button>
              <el-button type="primary" link size="small" @click="showDialog('edit', data)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(data.id)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入分类编码" />
        </el-form-item>
        <el-form-item label="上级分类" v-if="form.parent_id">
          <el-input :value="parentName" disabled />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { Category } from '@/types'

const categoryStore = useCategoryStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)

const form = reactive({
  name: '',
  code: '',
  parent_id: undefined as number | undefined,
  description: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增分类' : '编辑分类')

const parentName = computed(() => {
  if (!form.parent_id) return ''
  function findName(cats: Category[], id: number): string {
    for (const cat of cats) {
      if (cat.id === id) return cat.name
      if (cat.children?.length) {
        const found = findName(cat.children, id)
        if (found) return found
      }
    }
    return ''
  }
  return findName(categoryStore.categories, form.parent_id)
})

function showDialog(mode: 'create' | 'edit', data?: Category) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    form.name = ''
    form.code = ''
    form.parent_id = data?.id ?? undefined
    form.description = ''
  } else {
    currentId.value = data!.id
    form.name = data!.name
    form.code = data!.code || ''
    form.parent_id = data!.parent_id ?? undefined
    form.description = data!.description || ''
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (dialogMode.value === 'create') {
          await categoryStore.create(form)
          ElMessage.success('创建成功')
        } else {
          await categoryStore.update(currentId.value!, form)
          ElMessage.success('保存成功')
        }
        dialogVisible.value = false
      } catch (error) {
        // Error handled by interceptor
      } finally {
        loading.value = false
      }
    }
  })
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该分类吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await categoryStore.remove(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  categoryStore.fetchTree()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-tree {
  padding: 10px 0;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.node-actions {
  display: flex;
  gap: 8px;
}
</style>
