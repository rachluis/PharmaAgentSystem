<template>
  <div class="login-container">
    <!-- Fluid Background Blobs -->
    <div class="shape-blob shape-1"></div>
    <div class="shape-blob shape-2"></div>
    
    <div class="content-wrapper">
      <!-- Left: Brand Area -->
      <div class="login-left hidden-xs-only">
        <div class="brand-content">
          <div class="logo-wrapper">
            <el-icon class="logo-icon rotating"><DataAnalysis /></el-icon>
          </div>
          <h1 class="brand-title">Pharma Intel</h1>
          <p class="brand-subtitle">医药市场智能分析与决策平台</p>
          
          <div class="features-list">
            <div class="feature-item" v-for="(item, index) in features" :key="index" :style="{ '--delay': index * 0.1 + 's' }">
              <div class="feature-icon">
                <component :is="item.icon" />
              </div>
              <div class="feature-text">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Login Form Area -->
      <div class="login-right">
        <div class="glass-card">
          <div class="form-header">
            <h2>欢迎回来 👋</h2>
            <p class="sub-text">请输入您的账号密码以访问系统</p>
          </div>

          <el-form 
            :model="form" 
            :rules="rules" 
            ref="formRef" 
            label-width="0"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username" :class="{ 'error-shake': shakeField === 'username' }">
              <div class="input-wrapper">
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                  :class="{ 'is-error': loginError }"
                  @focus="clearError"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <el-form-item prop="password" :class="{ 'error-shake': shakeField === 'password' }">
              <div class="input-wrapper">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  class="custom-input"
                  :class="{ 'is-error': loginError }"
                  @focus="clearError"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <!-- 错误提示 -->
            <div v-if="loginError && errorMessage" class="error-message">
              <el-icon class="error-icon"><Warning /></el-icon>
              <span>{{ errorMessage }}</span>
            </div>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <el-link type="primary" :underline="false" @click="showForgotPassword = true">忘记密码?</el-link>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                :disabled="loading"
                @click="handleLogin"
              >
                <template v-if="!loading">
                  <span>立即登录</span>
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </template>
                <template v-else>
                  <span>登录中...</span>
                </template>
              </el-button>
            </el-form-item>

            <div class="form-footer">
              <span>还没有账号？</span>
              <el-link type="primary" @click="showRegister = true">立即注册</el-link>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <!-- Register Dialog -->
    <el-dialog 
      v-model="showRegister" 
      title="创建新账号" 
      width="450px"
      align-center
      class="custom-dialog register-dialog"
      :close-on-click-modal="false"
    >
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" :prefix-icon="User" placeholder="3-20个字符，字母/数字/下划线"/>
        </el-form-item>
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="registerForm.email" :prefix-icon="Message" placeholder="用于找回密码"/>
        </el-form-item>
        <el-form-item label="真实姓名" prop="full_name">
          <el-input v-model="registerForm.full_name" :prefix-icon="Postcard" placeholder="选填"/>
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="registerForm.phone" :prefix-icon="Iphone" placeholder="选填"/>
        </el-form-item>
        <el-form-item label="个人简介" prop="bio">
          <el-input v-model="registerForm.bio" type="textarea" placeholder="选填，介绍下自己"/>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password :prefix-icon="Lock" placeholder="至少6位"/>
          <PasswordStrength :password="registerForm.password" :show-details="true" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" show-password :prefix-icon="Lock" placeholder="再次输入密码"/>
        </el-form-item>
        
        <el-form-item prop="agreement">
          <el-checkbox v-model="registerForm.agreement">
            我已阅读并同意 <el-link type="primary">用户协议</el-link> 和 <el-link type="primary">隐私政策</el-link>
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showRegister = false">取 消</el-button>
          <el-button type="primary" :loading="registerLoading" @click="handleRegister">
            确认注册
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Forgot Password Dialog -->
    <el-dialog 
      v-model="showForgotPassword" 
      title="找回密码" 
      width="400px"
      align-center
      class="custom-dialog"
    >
      <el-steps :active="forgotStep" finish-status="success" align-center class="mb-4">
        <el-step title="验证身份" />
        <el-step title="重置密码" />
      </el-steps>

      <!-- Step 1: Verify Email -->
      <div v-if="forgotStep === 0">
        <p class="dialog-desc">请输入您的注册邮箱，我们将验证您的身份。</p>
        <el-form :model="forgotForm" :rules="forgotRules" ref="forgotFormRef">
          <el-form-item prop="email">
            <el-input v-model="forgotForm.email" prefix-icon="Message" placeholder="请输入注册邮箱" />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: Reset Password -->
      <div v-if="forgotStep === 1">
        <p class="dialog-desc">请设置您的新密码。</p>
        <el-form :model="resetForm" :rules="resetRules" ref="resetFormRef" label-position="top">
          <el-form-item label="新密码" prop="password">
            <el-input v-model="resetForm.password" type="password" show-password prefix-icon="Lock" />
            <PasswordStrength :password="resetForm.password" />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="resetForm.confirmPassword" type="password" show-password prefix-icon="Lock" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showForgotPassword = false" v-if="forgotStep === 0">取 消</el-button>
          <el-button type="primary" :loading="forgotLoading" @click="handleForgotNext">
            {{ forgotStep === 0 ? '下一步' : '确认重置' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  User, Lock, DataAnalysis, Monitor, 
  TrendCharts, Cpu, ArrowRight, Message, Postcard, Iphone, Warning
} from '@element-plus/icons-vue'
import { login, register, type RegisterRequest } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import PasswordStrength from '@/components/PasswordStrength.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const forgotFormRef = ref<FormInstance>()
const resetFormRef = ref<FormInstance>()

const loading = ref(false)
const registerLoading = ref(false)
const forgotLoading = ref(false)
const showRegister = ref(false)
const showForgotPassword = ref(false)
const rememberMe = ref(false)
const loginError = ref(false)
const errorMessage = ref('')
const shakeField = ref('')
const forgotStep = ref(0)

// 初始化：检查是否已登录
onMounted(() => {
  if (userStore.isAuthenticated) {
    router.push(route.query.redirect as string || '/dashboard')
  }
  
  // 恢复记住我状态
  rememberMe.value = userStore.rememberMe
  if (rememberMe.value && userStore.user) {
    form.username = userStore.user.username
  }
})

// Features list
const features = [
  { icon: Monitor, title: '全景画像', desc: '360° 医生行为数据深度分析' },
  { icon: Cpu, title: 'AI 驱动', desc: '基于 LLM 的智能策略生成引擎' },
  { icon: TrendCharts, title: '精准营销', desc: '数据支撑的资源投放优化' },
]

// Login Form
const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// Register Form
const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  phone: '',
  bio: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const validatePass2 = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validatePass2, trigger: 'blur' }
  ],
  agreement: [
    { 
      validator: (_rule, value, callback) => {
        if (!value) callback(new Error('请阅读并同意用户协议'))
        else callback()
      }, 
      trigger: 'change' 
    }
  ]
}

// Forgot Password Forms
const forgotForm = reactive({ email: '' })
const resetForm = reactive({ password: '', confirmPassword: '' })

const forgotRules = {
  email: [
    { required: true, message: '请输入注册邮箱', trigger: 'blur' },
    { type: 'email', message: '格式不正确', trigger: 'blur' }
  ]
}

const validateResetPass2 = (_rule: any, value: string, callback: any) => {
  if (value !== resetForm.password) callback(new Error('两次密码不一致'))
  else callback()
}

const resetRules = {
  password: [{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }],
  confirmPassword: [{ validator: validateResetPass2, trigger: 'blur' }]
}

// Methods
const clearError = () => {
  loginError.value = false
  errorMessage.value = ''
  shakeField.value = ''
}

const triggerShake = (field: string) => {
  shakeField.value = field
  setTimeout(() => {
    shakeField.value = ''
  }, 500)
}

const handleLogin = async () => {
  if (!form.username) {
    triggerShake('username')
    return
  }
  if (!form.password) {
    triggerShake('password')
    return
  }

  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  loginError.value = false
  errorMessage.value = ''
  
  try {
    const res = await login({
      username: form.username,
      password: form.password
    })
    
    // 设置记住我
    userStore.setRememberMe(rememberMe.value)
    
    // 保存 token
    userStore.setToken(res.access_token)
    
    // 如果后端返回了用户信息，直接使用；否则获取
    if (res.user) {
      userStore.setUser(res.user)
    } else {
      // 获取用户信息
      await userStore.fetchUserInfo()
    }
    
    ElMessage.success({
      message: `登录成功，欢迎回来，${userStore.userName}！`,
      duration: 2000,
      showClose: true
    })
    
    // 跳转到目标页面或默认页面
    const redirect = route.query.redirect as string || '/dashboard'
    setTimeout(() => {
      router.push(redirect)
    }, 500)
    
  } catch (error: any) {
    console.error('Login failed:', error)
    loginError.value = true
    
    // 更详细的错误提示
    if (error.response?.status === 401) {
      errorMessage.value = '用户名或密码错误，请重试'
    } else if (error.response?.status === 403) {
      errorMessage.value = '账号已被禁用，请联系管理员'
    } else if (error.response?.status === 429) {
      errorMessage.value = '登录尝试过于频繁，请稍后再试'
    } else {
      errorMessage.value = error.response?.data?.detail || error.message || '登录失败，请检查网络连接'
    }
    
    triggerShake('username')
    triggerShake('password')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  registerLoading.value = true
  try {
    const registerData: RegisterRequest = {
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    }
    
    if (registerForm.full_name) registerData.full_name = registerForm.full_name
    if (registerForm.phone) registerData.phone = registerForm.phone
    if (registerForm.bio) registerData.bio = registerForm.bio
    
    await register(registerData)
    
    ElMessage.success({
      message: '注册成功！请使用新账号登录',
      duration: 3000
    })
    
    showRegister.value = false
    
    // 自动填充用户名
    form.username = registerForm.username
    form.password = ''
    
    // 重置注册表单
    registerFormRef.value?.resetFields()
    Object.assign(registerForm, {
      username: '',
      email: '',
      full_name: '',
      phone: '',
      bio: '',
      password: '',
      confirmPassword: '',
      agreement: false
    })
    
  } catch (error: any) {
    console.error('Register failed:', error)
    const errorMsg = error.response?.data?.detail || error.message || '注册失败，请重试'
    ElMessage.error(errorMsg)
  } finally {
    registerLoading.value = false
  }
}

const handleForgotNext = async () => {
  if (forgotStep.value === 0) {
    const valid = await forgotFormRef.value?.validate().catch(() => false)
    if (!valid) return
    
    forgotLoading.value = true
    // Simulate check email
    setTimeout(() => {
      forgotLoading.value = false
      forgotStep.value = 1
      ElMessage.success('验证成功，请重置密码')
    }, 1000)
  } else {
    const valid = await resetFormRef.value?.validate().catch(() => false)
    if (!valid) return
    
    forgotLoading.value = true
    // Simulate reset password
    setTimeout(() => {
      forgotLoading.value = false
      ElMessage.success('密码重置成功，请登录')
      showForgotPassword.value = false
      forgotStep.value = 0
      resetForm.password = ''
      resetForm.confirmPassword = ''
    }, 1000)
  }
}
</script>

<style scoped>
/* 使用全局变量替换硬编码颜色 */
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--background);
  /* Fallback or specific gradient for login page */
  background-image: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,0.1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,0.1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,0.1) 0, transparent 50%);
  position: relative;
  overflow: hidden;
}

/* 动态流体球效果 - Adjusted for theme colors */
.shape-blob {
  background: var(--primary);
  height: 200px;
  width: 200px;
  border-radius: 30% 50% 20% 40%;
  animation: 
    transform 20s ease-in-out infinite both alternate,
    movement_one 40s ease-in-out infinite both;
  opacity: 0.2;
  position: absolute;
  left: 70%;
  top: 50%;
  filter: blur(40px);
  z-index: 1;
}
.shape-2 {
  height: 350px;
  width: 350px;
  background: #764ba2;
  left: 10%;
  top: 20%;
  animation-name: transform, movement_two;
  opacity: 0.2;
}

@keyframes movement_one {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  20% { transform: translate(20%, -10%) rotate(20deg); }
  40% { transform: translate(-10%, 20%) rotate(-10deg); }
  60% { transform: translate(10%, 20%) rotate(10deg); }
  80% { transform: translate(-20%, -20%) rotate(-20deg); }
}

@keyframes movement_two {
  0% { transform: translate(0, 0) rotate(0deg) scale(1); }
  20% { transform: translate(-20%, 10%) rotate(-20deg) scale(1.1); }
  40% { transform: translate(10%, -20%) rotate(10deg) scale(0.9); }
  60% { transform: translate(-10%, -20%) rotate(-10deg) scale(1.05); }
  80% { transform: translate(20%, 20%) rotate(20deg) scale(0.95); }
  100% { transform: translate(0, 0) rotate(0deg) scale(1); }
}

@keyframes transform {
  0%, 100% { border-radius: 33% 67% 70% 30% / 30% 30% 70% 70%; } 
  20% { border-radius: 37% 63% 51% 49% / 37% 65% 35% 63%; } 
  40% { border-radius: 36% 64% 64% 36% / 64% 48% 52% 36%; } 
  60% { border-radius: 37% 63% 51% 49% / 30% 30% 70% 70%; } 
  80% { border-radius: 40% 60% 42% 58% / 41% 51% 49% 59%; } 
}

/* Shake Animation */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.error-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

/* Content Layout */
.content-wrapper {
  display: flex;
  width: 1000px;
  height: 600px;
  background: var(--card); /* Using global card var */
  /* backdrop-filter: blur(20px); Not supported on all browsers with bg color, using opacity in rgba if needed or just solid card */
  border-radius: 24px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  z-index: 2;
  overflow: hidden;
}

/* Left Brand Area */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, var(--sidebar) 0%, #1a3a5c 100%); /* Using sidebar/accent colors or specific gradient */
  padding: 60px;
  display: flex;
  flex-direction: column;
  color: white;
  position: relative;
}

.logo-wrapper {
  margin-bottom: 20px;
}

.logo-icon {
  font-size: 48px;
  color: var(--primary);
}

.brand-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 10px 0;
  letter-spacing: 1px;
}

.brand-subtitle {
  font-size: 16px;
  opacity: 0.8;
  margin-bottom: 60px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  opacity: 0;
  animation: slideInLeft 0.5s ease forwards;
  animation-delay: var(--delay);
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: var(--primary);
  transition: all 0.3s ease;
}

.feature-item:hover .feature-icon {
  background: var(--primary);
  color: white;
  transform: scale(1.1);
}

.feature-text h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.feature-text p {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

/* Right Form Area */
.login-right {
  flex: 1;
  background: var(--card);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.glass-card {
  width: 100%;
  max-width: 380px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 24px;
  color: var(--foreground);
  margin: 0 0 8px 0;
}

.sub-text {
  color: var(--muted-foreground);
  font-size: 14px;
}

/* Custom Input Styles */
:deep(.el-input__wrapper) {
  background-color: var(--secondary);
  box-shadow: none !important;
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  padding: 8px 11px;
  border-radius: 8px;
}

:deep(.el-input__wrapper:hover) {
  border-color: var(--primary);
  background-color: var(--card);
}

:deep(.el-input__wrapper.is-focus) {
  background-color: var(--card);
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.1) !important;
}

/* Specific error style */
:deep(.is-error .el-input__wrapper) {
  border-color: #ef4444;
  background-color: #fef2f2;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97);
}

:deep(.is-error .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1) !important;
}

.input-wrapper {
  margin-bottom: 5px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 14px;
}

.form-options :deep(.el-checkbox__label) {
  color: var(--muted-foreground);
  font-size: 14px;
}

.form-options :deep(.el-link) {
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-btn:not(:disabled):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.login-btn:not(:disabled):active {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-btn .el-icon--right {
  margin-left: 8px;
  transition: transform 0.3s ease;
}

.login-btn:not(:disabled):hover .el-icon--right {
  transform: translateX(4px);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--muted-foreground);
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  animation: slideDown 0.3s ease;
}

.error-icon {
  font-size: 18px;
  flex-shrink: 0;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .content-wrapper {
    width: 90%;
    height: auto;
    flex-direction: column;
  }
  
  .login-left {
    display: none;
  }
  
  .login-right {
    padding: 60px 40px;
  }
  
  .shape-blob {
    opacity: 0.1;
  }
}

.mb-4 {
  margin-bottom: 16px;
}

.dialog-desc {
  margin-bottom: 20px;
  color: var(--muted-foreground);
  font-size: 14px;
}

.register-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
  padding-bottom: 10px;
}
</style>