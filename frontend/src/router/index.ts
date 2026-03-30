import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Extend route meta type
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    adminOnly?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    meta: { title: '登录' },
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        meta: { title: '仪表盘' },
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue')
      },
      {
        path: 'assets',
        meta: { title: '资产管理' },
        name: 'Assets',
        component: () => import('@/views/assets/AssetList.vue')
      },
      {
        path: 'assets/create',
        meta: { title: '新增资产' },
        name: 'AssetCreate',
        component: () => import('@/views/assets/AssetForm.vue')
      },
      {
        path: 'assets/:id/edit',
        meta: { title: '编辑资产' },
        name: 'AssetEdit',
        component: () => import('@/views/assets/AssetForm.vue')
      },
      {
        path: 'categories',
        meta: { title: '分类管理' },
        name: 'Categories',
        component: () => import('@/views/categories/CategoryList.vue')
      },
      {
        path: 'suppliers',
        meta: { title: '供应商管理' },
        name: 'Suppliers',
        component: () => import('@/views/suppliers/SupplierList.vue')
      },
      {
        path: 'purchases',
        meta: { title: '采购管理' },
        name: 'Purchases',
        component: () => import('@/views/purchases/PurchaseList.vue')
      },
      {
        path: 'users',
        meta: { title: '用户管理' },
        name: 'Users',
        component: () => import('@/views/users/UserList.vue')
      },
      {
        path: 'settings',
        meta: { title: '系统设置' },
        name: 'Settings',
        component: () => import('@/views/settings/Settings.vue')
      },
      {
        path: 'departments',
        meta: { title: '部门管理' },
        name: 'Departments',
        component: () => import('@/views/departments/DepartmentList.vue')
      },
      {
        path: 'audit',
        meta: { title: '审计日志' },
        name: 'AuditLog',
        component: () => import('@/views/audit/AuditLogList.vue'),
        meta: { requiresAuth: true, adminOnly: true }
      },
      {
        path: 'approvals',
        meta: { title: '我的申请' },
        name: 'Approvals',
        component: () => import('@/views/approvals/ApprovalList.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'approval-instances/:id',
        meta: { title: '审批详情' },
        name: 'ApprovalInstanceDetail',
        component: () => import('@/views/approvals/ApprovalInstanceDetail.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'approval-flows',
        meta: { title: '审批流程' },
        name: 'ApprovalFlowConfig',
        component: () => import('@/views/approvals/ApprovalFlowConfig.vue'),
        meta: { requiresAuth: true, adminOnly: true }
      },
      {
        path: 'reports',
        meta: { title: '统计报表' },
        name: 'AssetReports',
        component: () => import('@/views/reports/AssetReports.vue'),
        meta: { requiresAuth: true, adminOnly: true }
      },
      {
        path: 'depreciation',
        meta: { title: '折旧管理' },
        name: 'Depreciation',
        component: () => import('@/views/reports/DepreciationReport.vue'),
        meta: { requiresAuth: true, adminOnly: true }
      },
      {
        path: 'assets/:id',
        meta: { title: '资产详情' },
        name: 'AssetDetail',
        component: () => import('@/views/assets/AssetDetail.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'asset-transfers',
        meta: { title: '资产调拨' },
        name: 'AssetTransfers',
        component: () => import('@/views/assets/AssetTransferList.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth !== false && !authStore.isLoggedIn()) {
    next('/login')
    return
  }
  
  if (to.path === '/login' && authStore.isLoggedIn()) {
    next('/')
    return
  }
  
  // Check admin-only routes
  if (to.meta.adminOnly) {
    // Ensure user data is loaded
    if (!authStore.user) {
      try {
        await authStore.fetchUser()
      } catch {
        next('/login')
        return
      }
    }
    
    if (!authStore.isAdmin) {
      // Non-admin trying to access admin page - redirect to dashboard
      next('/dashboard')
      return
    }
  }
  
  next()
})

// Dynamic document title
router.afterEach((to) => {
  const title = to.meta?.title
    ? to.meta.title + ' - IT资产管理系统'
    : 'IT资产管理系统';
  document.title = title;
});

export default router
