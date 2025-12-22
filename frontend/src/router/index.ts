import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

// Views
import Login from '@/views/Login.vue'
import MainLayout from '@/layout/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Dashboard', requiresAuth: true }
      },
      {
        path: 'analysis',
        name: 'analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '聚类分析', requiresAuth: true }
      },
      {
        path: 'doctors',
        name: 'doctors',
        component: () => import('@/views/doctors/DoctorList.vue'),
        meta: { title: '医生列表', requiresAuth: true }
      },
      {
        path: 'doctors/:npi',
        name: 'doctor-detail',
        component: () => import('@/views/doctors/DoctorDetail.vue'),
        meta: { title: '医生详情', requiresAuth: true }
      },
      {
        path: 'reports',
        name: 'reports',
        component: () => import('@/views/reports/ReportList.vue'),
        meta: { title: 'AI报告', requiresAuth: true }
      },
      {
        path: 'reports/:id',
        name: 'report-detail',
        component: () => import('@/views/reports/ReportDetail.vue'),
        meta: { title: '报告详情', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/settings/Settings.vue'),
        meta: { title: '个人设置', requiresAuth: true }
      },
      {
        path: 'system/logs',
        name: 'system-logs',
        component: () => import('@/views/system/Logs.vue'),
        meta: { title: '系统日志', requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 初始化用户状态
  if (!userStore.user && userStore.token) {
    try {
      await userStore.fetchUserInfo()
    } catch {
      userStore.clearUser()
    }
  }
  
  // 需要认证的路由
  if (to.meta.requiresAuth) {
    if (!userStore.isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } 
  // 已登录用户访问登录页，重定向到首页
  else if (to.path === '/login' && userStore.isAuthenticated) {
    next(from.fullPath || '/dashboard')
  } 
  else {
    next()
  }
})

export default router
