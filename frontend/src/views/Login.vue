<template>
  <div class="login-container">
    <!-- 动态背景球体 -->
    <div class="shape-blob shape-1"></div>
    <div class="shape-blob shape-2"></div>
    
    <div class="content-wrapper">
      <!-- 左侧：品牌展示区 -->
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

      <!-- 右侧：登录表单区 -->
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
          >
            <el-form-item prop="username">
              <div class="input-wrapper">
                <el-input
                  v-model="form.username"
                  placeholder="请输入用户名"
                  class="custom-input"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-wrapper">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="请输入密码"
                  show-password
                  class="custom-input"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <el-link type="primary" :underline="false">忘记密码?</el-link>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '立即登录' }}
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
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

    <!-- 注册弹窗 (保持原有逻辑，优化样式) -->
    <el-dialog 
      v-model="showRegister" 
      title="创建新账号" 
      width="400px"
      align-center
      class="custom-dialog"
    >
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" prefix-icon="User" placeholder="设置用户名"/>
        </el-form-item>
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="registerForm.email" prefix-icon="Message" placeholder="example@email.com"/>
        </el-form-item>
        <el-form-item label="真实姓名" prop="full_name">
          <el-input v-model="registerForm.full_name" prefix-icon="Postcard" placeholder="您的称呼"/>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" show-password prefix-icon="Lock" placeholder="设置密码"/>
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
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { 
  User, Lock, DataAnalysis, Monitor, 
  TrendCharts, Cpu, ArrowRight
} from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const formRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)
const rememberMe = ref(false)

// 左侧特性列表
const features = [
  { icon: Monitor, title: '全景画像', desc: '360° 医生行为数据深度分析' },
  { icon: Cpu, title: 'AI 驱动', desc: '基于 LLM 的智能策略生成引擎' },
  { icon: TrendCharts, title: '精准营销', desc: '数据支撑的资源投放优化' },
]

const form = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  full_name: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名3-50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    const formData = new URLSearchParams()
    formData.append('username', form.username)
    formData.append('password', form.password)
    
    const res: any = await request.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error: any) {
    console.error('Login failed:', error)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate().catch(() => false)
  if (!valid) return
  
  registerLoading.value = true
  try {
    await request.post('/auth/register', registerForm)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    form.username = registerForm.username
    form.password = ''
  } catch (error: any) {
    console.error('Register failed:', error)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
/* 容器与动态背景 */
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  background-image: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
  position: relative;
  overflow: hidden;
}

/* 动态流体球效果 */
.shape-blob {
  background: #2696e9;
  height: 200px;
  width: 200px;
  border-radius: 30% 50% 20% 40%;
  animation: 
    transform 20s ease-in-out infinite both alternate,
    movement_one 40s ease-in-out infinite both;
  opacity: .5;
  position: absolute;
  left: 70%;
  top: 50%;
  filter: blur(40px);
  z-index: 1;
}
.shape-2 {
  height: 350px;
  width: 350px;
  background: #4e54c8;
  left: 10%;
  top: 20%;
  animation-name: transform, movement_two;
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

/* 内容布局 */
.content-wrapper {
  display: flex;
  width: 1000px;
  height: 600px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  border: 1px solid rgba(255, 255, 255, 0.18);
  z-index: 2;
  overflow: hidden;
}

/* 左侧品牌区 */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
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
  color: #64b5f6;
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

/* 左侧特性列表动画 */
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
  color: #64b5f6;
  transition: all 0.3s ease;
}

.feature-item:hover .feature-icon {
  background: #64b5f6;
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

/* 右侧表单区 */
.login-right {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.glass-card {
  width: 100%;
  max-width: 360px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h2 {
  font-size: 24px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.sub-text {
  color: #6b7280;
  font-size: 14px;
}

/* 输入框样式重写 */
:deep(.el-input__wrapper) {
  background-color: #f3f4f6;
  box-shadow: none !important;
  border: 1px solid transparent;
  transition: all 0.3s ease;
  padding: 8px 11px;
}

:deep(.el-input__wrapper.is-focus) {
  background-color: white;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
}

.input-wrapper {
  margin-bottom: 5px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #6b7280;
}

/* 动画定义 */
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

/* 响应式调整 */
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
}
</style>