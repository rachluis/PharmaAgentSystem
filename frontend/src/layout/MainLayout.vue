<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside 
      :width="themeStore.sidebarCollapsed ? '64px' : '240px'" 
      class="sidebar"
    >
      <!-- Logo -->
      <div class="logo">
        <el-icon v-if="themeStore.sidebarCollapsed" :size="28" color="#409EFF">
          <Monitor />
        </el-icon>
        <template v-else>
          <el-icon :size="24" color="#409EFF"><Monitor /></el-icon>
          <h2>Pharma Intel</h2>
        </template>
      </div>
      
      <!-- Menu -->
      <el-scrollbar class="sidebar-scrollbar">
        <el-menu
          router
          :default-active="$route.path"
          :collapse="themeStore.sidebarCollapsed"
          :collapse-transition="false"
          background-color="var(--sidebar)"
          text-color="var(--sidebar-foreground)"
          active-text-color="#409EFF"
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
          
          <el-sub-menu index="system">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>系统工具</span>
            </template>
            <el-menu-item index="/system/logs">系统日志</el-menu-item>
            <el-menu-item index="/settings">用户管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
      
      <!-- Bottom Actions -->
      <div class="sidebar-footer">
        <el-tooltip :content="themeStore.sidebarCollapsed ? '设置' : ''" placement="right">
          <div class="footer-item" @click="showSettings = true">
            <el-icon :size="18"><Setting /></el-icon>
            <span v-if="!themeStore.sidebarCollapsed">设置</span>
          </div>
        </el-tooltip>
        
        <el-tooltip :content="themeStore.sidebarCollapsed ? '展开' : '收起'" placement="right">
          <div class="footer-item" @click="themeStore.toggleSidebar()">
            <el-icon :size="18">
              <Fold v-if="!themeStore.sidebarCollapsed" />
              <Expand v-else />
            </el-icon>
            <span v-if="!themeStore.sidebarCollapsed">收起</span>
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
          <!-- Theme Toggle -->
          <el-tooltip :content="themeStore.theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'">
            <el-button 
              circle 
              @click="themeStore.toggleTheme()"
              class="theme-toggle"
            >
              <el-icon>
                <Sunny v-if="themeStore.theme === 'dark'" />
                <Moon v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          
          <!-- User Dropdown -->
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown">
              <el-avatar :size="32" :src="userAvatar" />
              <span class="username">{{ username }}</span>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon> 个人信息
                </el-dropdown-item>
                <el-dropdown-item command="change-password">
                  <el-icon><Lock /></el-icon> 修改密码
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
          <span>深色模式</span>
          <el-switch 
            v-model="isDarkMode" 
            @change="themeStore.toggleTheme()"
          />
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
  Setting, Fold, Expand, Monitor, SwitchButton,
  Tools, Sunny, Moon, Lock
} from "@element-plus/icons-vue"
import { ElMessage } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import request from '@/api/request'

const router = useRouter()
const route = useRoute()
const themeStore = useThemeStore()
const userStore = useUserStore()

// Settings drawer
const showSettings = ref(false)

// Dark mode computed
const isDarkMode = computed({
  get: () => themeStore.theme === 'dark',
  set: () => {} // Handled by switch @change
})

// User info
const username = computed(() => userStore.user?.full_name || userStore.user?.username || 'Admin')
const userAvatar = computed(() => userStore.user?.avatar_url || 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')

// Current page name
const pageNames: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/doctors': '医生管理',
  '/analysis': '聚类分析',
  '/reports': 'AI报告',
  '/settings': '个人设置',
  '/data/import': '数据导入',
  '/data/export': '数据导出',
  '/system/logs': '系统日志',
  '/system/users': '用户管理'
}
const currentPageName = computed(() => pageNames[route.path] || '页面')

// Methods
const handleCommand = (command: string) => {
  if (command === 'logout') {
    request.post('/auth/logout').finally(() => {
        userStore.clearUser()
        ElMessage.success('已退出登录')
        router.push('/login')
    })
  } else if (command === 'profile') {
    router.push('/settings?tab=profile')
  } else if (command === 'change-password') {
    router.push('/settings?tab=security')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100svh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  background-color: var(--sidebar);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  overflow: hidden;
  border-right: 1px solid var(--sidebar-border);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: var(--sidebar-accent);
  border-bottom: 1px solid var(--sidebar-border);
  padding: 0 20px;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  color: var(--sidebar-foreground);
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-scrollbar {
  flex: 1;
  height: 0;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

/* Sidebar Footer */
.sidebar-footer {
  border-top: 1px solid var(--sidebar-border);
  padding: 8px 0;
}

.footer-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: var(--sidebar-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.footer-item:hover {
  color: var(--sidebar-foreground);
  background-color: var(--sidebar-accent);
}

/* Main Container */
.main-container {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: var(--background);
}

/* Header */
.header {
  background-color: var(--card);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  border: 1px solid var(--border);
  background-color: var(--card);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius);
  transition: background-color 0.2s;
}

.user-dropdown:hover {
  background-color: var(--accent);
}

.username {
  font-size: 14px;
  color: var(--foreground);
}

/* Main Content */
.main-content {
  background-color: var(--background);
  padding: 20px;
  overflow-y: auto;
  height: calc(100svh - 60px);
}

/* Settings Drawer */
.settings-section {
  padding: 0 16px;
}

.settings-section h4 {
  margin: 16px 0 12px;
  font-size: 14px;
  color: var(--muted-foreground);
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
</style>
