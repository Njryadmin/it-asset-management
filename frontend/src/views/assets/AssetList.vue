<template>
  <div class="asset-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资产管理</span>
          <el-button type="primary" @click="$router.push('/assets/create')">
            <el-icon><Plus /></el-icon>
            新增资产
          </el-button>
        </div>
      </template>

      <!-- Search filters -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="assetStore.params.keyword" placeholder="搜索名称/编号/序列号" clearable @clear="search" @keyup.enter="search" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="assetStore.params.category_id" placeholder="选择分类" clearable @change="search">
            <el-option v-for="cat in flatCategories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="assetStore.params.status" placeholder="选择状态" clearable @change="search">
            <el-option label="使用中" value="in_use" />
            <el-option label="闲置" value="idle" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="已退役" value="retired" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- Table -->
      <el-table :data="assetStore.assets" v-loading="assetStore.loading" style="width: 100%">
        <el-table-column prop="name" label="资产名称" min-width="150" />
        <el-table-column prop="asset_code" label="资产编号" width="140" />
        <el-table-column prop="serial_number" label="序列号" width="140" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="purchase_price" label="购买价格" width="100">
          <template #default="{ row }">
            {{ row.purchase_price ? `¥${row.purchase_price}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="购买日期" width="120">
          <template #default="{ row }">
            {{ row.purchase_date ? dayjs(row.purchase_date).format('YYYY-MM-DD') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" width="160">
          <template #default="{ row }">
            {{ dayjs(row.created_at).format('YYYY-MM-DD HH:mm') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="$router.push(`/assets/${row.id}/edit`)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="assetStore.params.page"
          :page-size="assetStore.params.page_size"
          :total="assetStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAssetStore } from '@/stores/assets'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()
const assetStore = useAssetStore()

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

const statusMap: Record<string, string> = {
  in_use: '使用中',
  idle: '闲置',
  maintenance: '维护中',
  retired: '已退役',
  scrapped: '已报废'
}

function statusLabel(status: string) {
  return statusMap[status] || status
}

function statusTagType(status: string) {
  const map: Record<string, any> = {
    in_use: 'success',
    idle: 'info',
    maintenance: 'warning',
    retired: 'danger',
    scrapped: 'info'
  }
  return map[status] || 'info'
}

async function search() {
  assetStore.params.page = 1
  await assetStore.fetchAssets()
}

async function reset() {
  assetStore.resetParams()
  await assetStore.fetchAssets()
}

async function handlePageChange(page: number) {
  assetStore.params.page = page
  await assetStore.fetchAssets()
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条资产记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await assetStore.deleteAsset(id)
    ElMessage.success('删除成功')
    await assetStore.fetchAssets()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(async () => {
  await assetStore.fetchOptions()
  await assetStore.fetchAssets()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
