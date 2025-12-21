import { defineStore } from 'pinia'

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
    user: JSON.parse(localStorage.getItem('user') || 'null') as UserInfo | null
  }),
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setUser(user: UserInfo) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    clearUser() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }
})
