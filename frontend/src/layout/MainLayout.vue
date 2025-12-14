<template>
  <el-container class="layout-container">
    <el-aside width="220px">
      <div class="logo">
        <h2>Pharma Intel</h2>
      </div>
      <el-menu
        router
        :default-active="$route.path"
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/doctors">
          <el-icon><User /></el-icon>
          <span>医生管理</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><DataLine /></el-icon>
          <span>聚类分析</span>
        </el-menu-item>
        <el-menu-item index="/reports">
          <el-icon><Document /></el-icon>
          <span>AI报告</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              Admin <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Odometer, DataLine, User, Document, ArrowDown } from "@element-plus/icons-vue" // Added ArrowDown
import { ElMessage } from 'element-plus'

const router = useRouter()

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
}
.el-aside {
  background-color: #001529;
  color: white;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #002140;
}
.logo h2 {
  margin: 0;
  font-size: 18px;
}
.el-header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.header-content {
  padding-right: 20px;
}
.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
