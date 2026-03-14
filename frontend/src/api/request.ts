import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const service = axios.create({
  baseURL: '/api/v1', // Matches backend API prefix
  timeout: 30000
})

// Request interceptor
service.interceptors.request.use(
  (config) => {
    // Add token if available (check both localStorage and sessionStorage)
    const userStore = useUserStore()
    const token = userStore.token || 
                  localStorage.getItem('token') || 
                  sessionStorage.getItem('token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response) => {
    // Return response data directly for convenience
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const msg = error.response?.data?.detail || error.message || '请求失败'
    
    // Handle 401 Unauthorized
    if (status === 401) {
      const userStore = useUserStore()
      userStore.clearUser()
      
      // 避免在登录页重复提示
      if (router.currentRoute.value.path !== '/login') {
        ElMessage.error('登录已过期，请重新登录')
        router.push({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath }
        })
      }
    } 
    // Handle 403 Forbidden
    else if (status === 403) {
      ElMessage.error('没有权限访问该资源')
    }
    // Handle 429 Too Many Requests
    else if (status === 429) {
      ElMessage.error('请求过于频繁，请稍后再试')
    }
    // Handle 500+ Server Errors
    else if (status >= 500) {
      ElMessage.error('服务器错误，请稍后再试')
    }
    // Other errors - only show message if not handled by component
    else if (status !== 401 && status !== 403) {
      // 不自动显示错误，让组件自己处理
      // ElMessage.error(msg)
    }
    
    return Promise.reject(error)
  }
)

export default service
