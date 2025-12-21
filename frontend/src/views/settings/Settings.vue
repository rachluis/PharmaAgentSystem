<template>
  <div class="settings-container">
    <el-card class="settings-card" shadow="never">
      <el-tabs tab-position="left" style="height: 100%" v-model="activeTab">
        
        <!-- Tab 1: Profile Settings -->
        <el-tab-pane label="基础设置" name="profile">
          <div class="tab-content">
            <h2 class="tab-title">个人资料</h2>
            <div class="profile-header">
                <el-avatar :size="80" :src="getFullAvatarUrl(form.avatar_url)" />
                <div class="upload-area">
                    <input 
                        type="file" 
                        ref="fileInput" 
                        accept="image/*" 
                        style="display: none" 
                        @change="handleFileChange" 
                    />
                    <el-button type="primary" size="small" :loading="uploading" @click="handleAvatarClick">更换头像</el-button>
                    <p class="tip-text">支持 JPG, PNG 格式，文件小于 2MB</p>
                </div>
            </div>

            <el-form :model="form" label-position="top" class="profile-form" ref="formRef" :rules="rules">
                <el-row :gutter="20">
                    <el-col :span="12">
                         <el-form-item label="用户名 (不可修改)">
                            <el-input v-model="form.username" disabled />
                        </el-form-item>
                    </el-col>
                    <el-col :span="12">
                         <el-form-item label="真实姓名" prop="full_name">
                            <el-input v-model="form.full_name" placeholder="请输入真实姓名" />
                        </el-form-item>
                    </el-col>
                </el-row>
                
                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-form-item label="电子邮箱" prop="email">
                            <el-input v-model="form.email" placeholder="example@domain.com" />
                        </el-form-item>
                    </el-col>
                     <el-col :span="12">
                        <el-form-item label="手机号码" prop="phone">
                            <el-input v-model="form.phone" placeholder="请输入手机号码" />
                        </el-form-item>
                    </el-col>
                </el-row>

                <el-form-item label="个人简介">
                    <el-input type="textarea" v-model="form.bio" :rows="4" placeholder="介绍一下你自己..." />
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" :loading="saving" @click="handleSaveProfile">保存修改</el-button>
                </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 2: Security Settings -->
        <el-tab-pane label="安全设置" name="security">
             <div class="tab-content">
                <h2 class="tab-title">修改密码</h2>
                <el-form :model="pwdForm" label-position="top" class="security-form" ref="pwdFormRef" :rules="pwdRules">
                    <el-form-item label="当前密码" prop="old_password">
                        <el-input type="password" v-model="pwdForm.old_password" show-password placeholder="请输入当前密码" />
                    </el-form-item>
                    <el-form-item label="新密码" prop="new_password">
                        <el-input type="password" v-model="pwdForm.new_password" show-password placeholder="请输入新密码" />
                    </el-form-item>
                    <el-form-item label="确认新密码" prop="confirm_password">
                        <el-input type="password" v-model="pwdForm.confirm_password" show-password placeholder="请再次输入新密码" />
                    </el-form-item>
                    
                    <el-form-item>
                        <el-button type="primary" :loading="pwdSaving" @click="handleChangePassword">更新密码</el-button>
                    </el-form-item>
                </el-form>
             </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getProfile, updateProfile, changePassword, uploadAvatar } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const activeTab = ref(route.query.tab?.toString() || 'profile')

// --- Profile Logic ---
const formRef = ref<FormInstance>()
const saving = ref(false)
const uploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const form = reactive({
    id: 0,
    username: '',
    full_name: '',
    email: '',
    phone: '',
    bio: '',
    avatar_url: ''
})

const getFullAvatarUrl = (url: string) => {
    if (!url) return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
    if (url.startsWith('http')) return url
    return `${import.meta.env.VITE_API_BASE_URL || '/api/v1'}${url}`.replace('/api/v1/uploads', '/uploads')
    // Fix path logic: Backend mounts /uploads at root, but avatar_url is stored as /uploads/avatars/xxx.
    // We need to construct full URL. 
    // If backend is localhost:8000, then http://localhost:8000/uploads/avatars/xxx
}

const rules = reactive<FormRules>({
    email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    full_name: [
        { required: true, message: '请输入真实姓名', trigger: 'blur' }
    ]
})

const fetchUserInfo = async () => {
    try {
        const user = await getProfile()
        Object.assign(form, {
            id: user.id,
            username: user.username,
            full_name: user.full_name || '',
            email: user.email,
            phone: user.phone || '',
            bio: user.bio || '',
            avatar_url: user.avatar_url || ''
        })
        // Also update store to be sure
        userStore.setUser(user as any)
    } catch (e) {
        console.error(e)
    }
}

const handleSaveProfile = async () => {
    if (!formRef.value) return
    await formRef.value.validate(async (valid) => {
        if (valid) {
            saving.value = true
            try {
                const updatedUser = await updateProfile({
                    full_name: form.full_name,
                    email: form.email,
                    phone: form.phone,
                    bio: form.bio,
                    avatar_url: form.avatar_url
                })
                ElMessage.success('个人资料已更新')
                
                // Update pinia store which handles localStorage
                userStore.setUser(updatedUser as any)
            } catch (e: any) {
                 ElMessage.error(e.response?.data?.detail || '保存失败')
            } finally {
                saving.value = false
            }
        }
    })
}

const handleAvatarClick = () => {
    fileInput.value?.click()
}

const handleFileChange = async (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
        const file = target.files[0]
        if (!file) return; // TS guard
        
        // Validate size (2MB)
        if (file.size > 2 * 1024 * 1024) {
            ElMessage.error('图片大小不能超过 2MB')
            return
        }
        
        uploading.value = true
        try {
            const user = await uploadAvatar(file)
            form.avatar_url = user.avatar_url || ''
            userStore.setUser(user as any)
            ElMessage.success('头像上传成功')
        } catch (e: any) {
            ElMessage.error(e.response?.data?.detail || '头像上传失败')
        } finally {
            uploading.value = false
            // Reset input
            if (fileInput.value) fileInput.value.value = ''
        }
    }
}

// --- Security Logic ---
const pwdFormRef = ref<FormInstance>()
const pwdSaving = ref(false)
const pwdForm = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
})

const validatePass2 = (_rule: any, value: string, callback: any) => {
    if (value === '') {
        callback(new Error('请再次输入密码'));
    } else if (value !== pwdForm.new_password) {
        callback(new Error('两次输入密码不一致!'));
    } else {
        callback();
    }
};

const pwdRules = reactive<FormRules>({
    old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
    new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度至少6位', trigger: 'blur' }],
    confirm_password: [{ validator: validatePass2, trigger: 'blur' }]
})

const handleChangePassword = async () => {
    if (!pwdFormRef.value) return
    await pwdFormRef.value.validate(async (valid) => {
        if (valid) {
            pwdSaving.value = true
            try {
                await changePassword({
                    old_password: pwdForm.old_password,
                    new_password: pwdForm.new_password
                })
                ElMessage.success('密码修改成功')
                pwdForm.old_password = ''
                pwdForm.new_password = ''
                pwdForm.confirm_password = ''
            } catch (e: any) {
                ElMessage.error(e.response?.data?.detail || '密码修改失败')
            } finally {
                pwdSaving.value = false
            }
        }
    })
}

onMounted(() => {
    fetchUserInfo()
})
</script>

<style scoped>
.settings-container {
    height: 100%;
    padding: 20px;
}

.settings-card {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.settings-card :deep(.el-card__body) {
    height: 100%;
    padding: 0;
}

.tab-content {
    padding: 20px 40px;
    max-width: 800px;
}

.tab-title {
    margin-top: 0;
    margin-bottom: 30px;
    font-size: 24px;
    font-weight: 600;
    color: var(--foreground);
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 40px;
}

.upload-area {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.tip-text {
    font-size: 12px;
    color: var(--muted-foreground);
    margin: 0;
}

.profile-form, .security-form {
    max-width: 600px;
}
</style>
