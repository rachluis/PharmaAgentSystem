import request from './request'

// Types
export interface User {
    id: number
    username: string
    email: string
    full_name: string | null
    phone: string | null
    bio: string | null
    role: string
    avatar_url: string | null
    is_active: boolean
}

export interface UserUpdate {
    full_name?: string
    email?: string
    phone?: string
    bio?: string
    avatar_url?: string
}

export interface PasswordChange {
    old_password: string
    new_password: string
}

// API Methods
export const getProfile = () => {
    return request<any, User>({
        url: '/auth/me',
        method: 'get'
    })
}

export const updateProfile = (data: UserUpdate) => {
    return request<any, User>({
        url: '/auth/profile',
        method: 'put',
        data
    })
}

export const changePassword = (data: PasswordChange) => {
    return request<any, any>({
        url: '/auth/change-password',
        method: 'post',
        data
    })
}

export const logout = () => {
    return request<any, any>({
        url: '/auth/logout',
        method: 'post'
    })
}

export const uploadAvatar = (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request<any, User>({
        url: '/auth/upload-avatar',
        method: 'post',
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        data: formData
    })
}
