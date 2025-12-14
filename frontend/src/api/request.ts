import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/api/v1', // Matches backend API prefix
  timeout: 30000
})

// Request interceptor
service.interceptors.request.use(
  (config) => {
    // Add token if available
    const token = localStorage.getItem('token')
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
    const msg = error.response?.data?.detail || error.message || 'Request Failed'
    
    // Handle 401 Unauthorized
    if (status === 401) {
      localStorage.removeItem('token')
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else {
      ElMessage.error(msg)
    }
    
    return Promise.reject(error)
  }
)

export default service
