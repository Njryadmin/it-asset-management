<template>
  <div class="category-list">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="page-title">分类管理</h3>
            <span class="category-count">共 {{ categoryStore.categories.length }} 个分类</span>
          </div>
          <div class="header-actions">
            <el-dropdown trigger="click" @command="handleExport">
              <el-button>
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="all">导出全部</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="showImportDialog = true">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="primary" @click="showDialog('create')">
              <el-icon><Plus /></el-icon>
              新增分类
            </el-button>
          </div>
        </div>
      </template>

      <!-- Search -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索分类名称..."
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- Category Tree -->
      <div class="category-container">
        <el-tree
          v-if="filteredCategories.length > 0"
          :data="filteredCategories"
          :props="{ label: 'name', children: 'children' }"
          default-expand-all
          node-key="id"
          class="category-tree"
          :expand-on-click-node="false"
        >
          <template #default="{ node, data }">
            <div class="tree-node-wrapper">
              <div class="node-content">
                <div class="node-icon" :style="{ background: getCategoryColor(data.id) }">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="node-info">
                  <span class="node-name">{{ data.name }}</span>
                  <span class="node-code" v-if="data.code">{{ data.code }}</span>
                </div>
              </div>
              <div class="node-actions">
                <el-button type="primary" link size="small" @click="showDialog('create', data)">
                  <el-icon><Plus /></el-icon>
                  添加子分类
                </el-button>
                <el-button type="primary" link size="small" @click="showDialog('edit', data)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDelete(data.id)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>

        <!-- Empty State -->
        <el-empty v-else-if="searchKeyword" description="未找到匹配的分类" />
        <el-empty v-else description="暂无分类数据" />
      </div>
    </el-card>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" class="custom-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入分类编码（可选）" />
        </el-form-item>
        <el-form-item label="上级分类" v-if="form.parent_id && parentName">
          <el-tag type="info">{{ parentName }}</el-tag>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog v-model="showImportDialog" title="导入分类" width="500px" class="custom-dialog">
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :action="importUrl"
        :headers="{ Authorization: `Bearer ${token}` }"
        :before-upload="beforeUpload"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
        accept=".csv"
        :auto-upload="false"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽CSV文件到此处 或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只能上传CSV文件，请先下载模板</div>
          <el-button size="small" type="primary" @click="downloadTemplate">下载模板</el-button>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="submitImport">确定导入</el-button>
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
import dayjs from 'dayjs'

const categoryStore = useCategoryStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentId = ref<number | null>(null)
const searchKeyword = ref('')
const token = localStorage.getItem('token') || ''
const importUrl = '/api/v1/categories/import'
const uploadRef = ref()
const showImportDialog = ref(false)

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

const filteredCategories = computed(() => {
  if (!searchKeyword.value) return categoryStore.categories
  
  function filterTree(cats: Category[]): Category[] {
    return cats.reduce((acc: Category[], cat) => {
      const nameMatch = cat.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
      const codeMatch = cat.code?.toLowerCase().includes(searchKeyword.value.toLowerCase())
      
      let children = cat.children ? filterTree(cat.children) : []
      
      if (nameMatch || codeMatch || children.length > 0) {
        acc.push({ ...cat, children })
      }
      return acc
    }, [])
  }
  
  return filterTree(categoryStore.categories)
})

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

// Generate consistent color for category based on id
function getCategoryColor(id: number): string {
  const colors = [
    '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#a371f7',
    '#909399', '#2eb872', '#ff8c00', '#00bcd4', '#ff5722'
  ]
  return colors[id % colors.length]
}

function showDialog(mode: 'create' | 'edit', data?: Category) {
  dialogMode.value = mode
  if (mode === 'create') {
    currentId.value = null
    Object.assign(form, {
      name: '',
      code: '',
      parent_id: data?.id ?? undefined,
      description: ''
    })
  } else {
    currentId.value = data!.id
    Object.assign(form, {
      name: data!.name,
      code: data!.code || '',
      parent_id: data!.parentId ?? undefined,
      description: data!.description || ''
    })
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
          await categoryStore.create(form as any)
          ElMessage.success('创建成功')
        } else {
          await categoryStore.update(currentId.value!, form as any)
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

async function handleExport(command: string) {
  try {
    const response = await fetch('/api/v1/categories/export', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `categories_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

function beforeUpload(file: any) {
  const isCSV = file.name.endsWith('.csv')
  if (!isCSV) {
    ElMessage.error('只能上传CSV文件')
  }
  return isCSV
}

function handleImportSuccess(response: any) {
  if (response.imported !== undefined) {
    ElMessage.success(`导入完成：成功${response.imported}条，跳过${response.skipped}条`)
    showImportDialog.value = false
    categoryStore.fetchTree()
  }
}

function handleImportError(error: any) {
  ElMessage.error('导入失败')
}

function submitImport() {
  uploadRef.value?.submit()
}

function downloadTemplate() {
  const template = '\ufeff分类名称,编码,上级分类ID,描述\n'
  const example = '电脑设备,,,办公用电脑设备\n台式机,DESKTOP,1,台式机分类'
  const blob = new Blob([template + example], { type: 'text/csv;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'category_template.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  categoryStore.fetchTree()
})
</script>

<style scoped>
.category-list {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0;
}

.main-card {
  border-radius: var(--radius-lg) !important;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--theme-text-primary);
}

.category-count {
  font-size: 13px;
  color: var(--theme-text-secondary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-input {
  max-width: 320px;
}

.category-container {
  min-height: 300px;
}

.category-tree {
  padding: 8px 0;
  background: transparent;
}

.tree-node-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 12px 16px;
  margin: 4px 0;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.tree-node-wrapper:hover {
  background: var(--theme-border-light);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.node-name {
  font-weight: 500;
  color: var(--theme-text-primary);
  font-size: 14px;
}

.node-code {
  font-size: 12px;
  color: var(--theme-text-secondary);
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.tree-node-wrapper:hover .node-actions {
  opacity: 1;
}

.custom-dialog :deep(.el-dialog) {
  border-radius: var(--radius-lg) !important;
  background: var(--theme-card);
}

.upload-demo {
  text-align: center;
}
</style>
