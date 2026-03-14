import { defineStore } from 'pinia'
import { getProfile } from '@/api/auth'
import type { User } from '@/api/auth'

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string | null
  avatar_url: string | null
  phone: string | null
  bio: string | null
  role: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null') as UserInfo | null,
    rememberMe: localStorage.getItem('rememberMe') === 'true'
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isAnalyst: (state) => state.user?.role === 'analyst' || state.user?.role === 'admin',
    userName: (state) => state.user?.full_name || state.user?.username || '用户'
  },
  
  actions: {
    setToken(token: string) {
      this.token = token
      if (this.rememberMe) {
        localStorage.setItem('token', token)
      } else {
        sessionStorage.setItem('token', token)
      }
    },
    
    setUser(user: UserInfo) {
      this.user = user
      if (this.rememberMe) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        sessionStorage.setItem('user', JSON.stringify(user))
      }
    },
    
    setRememberMe(remember: boolean) {
      this.rememberMe = remember
      localStorage.setItem('rememberMe', String(remember))
    },
    
    async fetchUserInfo() {
      try {
        const user = await getProfile()
        this.setUser(user)
        return user
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        this.clearUser()
        throw error
      }
    },
    
    clearUser() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('rememberMe')
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
    },
    
    // 初始化时从存储中恢复状态
    init() {
      // 先恢复 rememberMe 状态
      const savedRememberMe = localStorage.getItem('rememberMe')
      if (savedRememberMe !== null) {
        this.rememberMe = savedRememberMe === 'true'
      }
      
      // 根据 rememberMe 状态恢复 token 和 user
      const token = this.rememberMe 
        ? localStorage.getItem('token')
        : sessionStorage.getItem('token')
      
      const userStr = this.rememberMe
        ? localStorage.getItem('user')
        : sessionStorage.getItem('user')
      
      if (token) {
        this.token = token
      }
      
      if (userStr) {
        try {
          this.user = JSON.parse(userStr) as UserInfo
        } catch {
          this.user = null
        }
      }
    }
  }
})
