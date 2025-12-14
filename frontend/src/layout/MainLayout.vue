<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapsed ? '64px' : '220px'" class="sidebar">
      <!-- Logo -->
      <div class="logo">
        <el-icon v-if="isCollapsed" :size="28" color="#409EFF"><Monitor /></el-icon>
        <h2 v-else>Pharma Intel</h2>
      </div>
      
      <!-- Menu -->
      <el-menu
        router
        :default-active="$route.path"
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#001529"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>Dashboard</template>
        </el-menu-item>
        <el-menu-item index="/doctors">
          <el-icon><User /></el-icon>
          <template #title>医生管理</template>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><DataLine /></el-icon>
          <template #title>聚类分析</template>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><Document /></el-icon>
          <template #title>AI报告</template>
        </el-menu-item>
      </el-menu>
      
      <!-- Bottom Actions -->
      <div class="sidebar-footer">
        <el-tooltip content="设置" placement="right" :disabled="!isCollapsed">
          <div class="footer-item" @click="showSettings = true">
            <el-icon :size="18"><Setting /></el-icon>
            <span v-if="!isCollapsed">设置</span>
          </div>
        </el-tooltip>
        <el-tooltip :content="isCollapsed ? '展开' : '收起'" placement="right">
          <div class="footer-item" @click="toggleCollapse">
            <el-icon :size="18">
              <Fold v-if="!isCollapsed" />
              <Expand v-else />
            </el-icon>
            <span v-if="!isCollapsed">收起</span>
          </div>
        </el-tooltip>
      </div>
    </el-aside>
    
    <!-- Main Content -->
    <el-container class="main-container">
      <!-- Header -->
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-dropdown">
              <el-avatar :size="32" :src="userAvatar" />
              <span class="username">{{ username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人信息
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- Page Content -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
    
    <!-- Settings Drawer -->
    <el-drawer v-model="showSettings" title="系统设置" :size="300">
      <div class="settings-section">
        <h4>主题设置</h4>
        <div class="setting-item">
          <span>主题色</span>
          <el-color-picker v-model="themeColor" :predefine="predefineColors" />
        </div>
        <div class="setting-item">
          <span>深色模式</span>
          <el-switch v-model="isDarkMode" />
        </div>
      </div>
    </el-drawer>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Odometer, DataLine, User, Document, ArrowDown,
  Setting, Fold, Expand, Monitor, SwitchButton 
} from "@element-plus/icons-vue"
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// Sidebar state
const isCollapsed = ref(false)
const showSettings = ref(false)

// Theme settings
const themeColor = ref('#409EFF')
const isDarkMode = ref(false)
const predefineColors = [
  '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
  '#1890ff', '#722ed1', '#13c2c2', '#eb2f96'
]

// User info
const username = computed(() => {
  const user = localStorage.getItem('user')
  if (user) {
    try {
      return JSON.parse(user).username || 'Admin'
    } catch {
      return 'Admin'
    }
  }
  return 'Admin'
})
const userAvatar = 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'

// Current page name
const pageNames: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/doctors': '医生管理',
  '/analysis': '聚类分析',
  '/reports': 'AI报告'
}
const currentPageName = computed(() => pageNames[route.path] || '页面')

// Methods
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    ElMessage.success('已退出登录')
    router.push('/login')
  } else if (command === 'profile') {
    ElMessage.info('功能开发中')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  background-color: #001529;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #002140;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.logo h2 {
  margin: 0;
  font-size: 18px;
  color: #fff;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
}
.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

/* Sidebar Footer */
.sidebar-footer {
  border-top: 1px solid rgba(255,255,255,0.1);
  padding: 8px 0;
}
.footer-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: rgba(255,255,255,0.65);
  cursor: pointer;
  transition: all 0.2s;
}
.footer-item:hover {
  color: #fff;
  background-color: rgba(255,255,255,0.05);
}

/* Main Container */
.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.header-left {
  display: flex;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
}
.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.username {
  font-size: 14px;
  color: #333;
}

/* Main Content */
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* Settings Drawer */
.settings-section {
  padding: 0 16px;
}
.settings-section h4 {
  margin: 16px 0 12px;
  font-size: 14px;
  color: #666;
}
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
</style>
