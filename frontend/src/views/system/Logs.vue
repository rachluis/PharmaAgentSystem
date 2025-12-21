<template>
  <div class="logs-container">
    <div class="page-header">
      <h2>系统日志</h2>
    </div>

    <el-tabs v-model="activeTab" class="log-tabs">
      <!-- Login Logs Tab -->
      <el-tab-pane label="登录日志" name="login">
        <div class="filter-bar">
          <el-input 
            v-model="loginFilter.username" 
            placeholder="搜索用户名" 
            prefix-icon="Search"
            style="width: 200px"
            clearable
            @clear="fetchLoginLogs"
            @keyup.enter="fetchLoginLogs"
          />
          <el-select v-model="loginFilter.status" placeholder="状态" clearable style="width: 120px" @change="fetchLoginLogs">
            <el-option label="成功" :value="1" />
            <el-option label="失败" :value="0" />
          </el-select>
          <el-button type="primary" @click="fetchLoginLogs">查询</el-button>
        </div>

        <el-table :data="loginLogs" v-loading="loginLoading" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="ip_address" label="IP地址" width="140" />
          <el-table-column prop="browser" label="浏览器/设备" min-width="200" show-overflow-tooltip/>
          <el-table-column prop="os" label="操作系统" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
                {{ scope.row.status === 1 ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="信息" width="150" show-overflow-tooltip />
          <el-table-column prop="login_time" label="登录时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.login_time) }}
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="loginPage.current"
            v-model:page-size="loginPage.size"
            :total="loginPage.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="fetchLoginLogs"
            @current-change="fetchLoginLogs"
          />
        </div>
      </el-tab-pane>

      <!-- Operation Logs Tab -->
      <el-tab-pane label="操作日志" name="operation">
        <div class="filter-bar">
          <el-input 
            v-model="opFilter.username" 
            placeholder="操作人" 
            prefix-icon="Search"
            style="width: 150px"
            clearable
            @keyup.enter="fetchOpLogs"
          />
          <el-select v-model="opFilter.module" placeholder="模块" clearable style="width: 120px">
            <el-option label="Auth" value="Auth" />
            <el-option label="Doctor" value="Doctor" />
            <el-option label="Analysis" value="Analysis" />
            <el-option label="Report" value="Report" />
          </el-select>
          <el-select v-model="opFilter.method" placeholder="方法" clearable style="width: 100px">
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
          <el-button type="primary" @click="fetchOpLogs">查询</el-button>
        </div>

        <el-table :data="opLogs" v-loading="opLoading" stripe style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="操作人" width="120" />
          <el-table-column prop="module" label="模块" width="100">
            <template #default="scope">
              <el-tag size="small" effect="plain">{{ scope.row.module || 'Unknown' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="方法" width="90">
            <template #default="scope">
              <el-tag :type="getMethodColor(scope.row.method)" size="small">
                {{ scope.row.method }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="path" label="路径" width="180" show-overflow-tooltip />
          <el-table-column prop="summary" label="简述" min-width="150" show-overflow-tooltip />
          <el-table-column prop="status" label="状态码" width="80">
             <template #default="scope">
              <span :class="scope.row.status >= 400 ? 'status-error' : 'status-success'">
                {{ scope.row.status }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="latency_ms" label="耗时(ms)" width="100" />
          <el-table-column prop="create_time" label="操作时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.create_time) }}
            </template>
          </el-table-column>
        </el-table>

         <div class="pagination">
          <el-pagination
            v-model:current-page="opPage.current"
            v-model:page-size="opPage.size"
            :total="opPage.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="fetchOpLogs"
            @current-change="fetchOpLogs"
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getLoginLogs, getOperationLogs } from '@/api/system'
import type { LoginLog, OperationLog } from '@/api/system'

const activeTab = ref('login')

// === Login Logs State ===
const loginLogs = ref<LoginLog[]>([])
const loginLoading = ref(false)
const loginFilter = reactive({
  username: '',
  status: undefined as number | undefined
})
const loginPage = reactive({
  current: 1,
  size: 20,
  total: 0
})

// === Operation Logs State ===
const opLogs = ref<OperationLog[]>([])
const opLoading = ref(false)
const opFilter = reactive({
  username: '',
  module: '',
  method: ''
})
const opPage = reactive({
  current: 1,
  size: 20,
  total: 0
})

// === Methods ===

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const getMethodColor = (method: string) => {
  switch (method) {
    case 'POST': return 'success'
    case 'PUT': return 'warning'
    case 'DELETE': return 'danger'
    default: return 'info'
  }
}

const fetchLoginLogs = async () => {
  loginLoading.value = true
  try {
    const res = await getLoginLogs({
      page: loginPage.current,
      size: loginPage.size,
      username: loginFilter.username || undefined,
      status: loginFilter.status
    })
    // @ts-ignore
    loginLogs.value = res.items
    // @ts-ignore
    loginPage.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    loginLoading.value = false
  }
}

const fetchOpLogs = async () => {
  opLoading.value = true
  try {
    const res = await getOperationLogs({
      page: opPage.current,
      size: opPage.size,
      username: opFilter.username || undefined,
      module: opFilter.module || undefined,
      method: opFilter.method || undefined
    })
    // @ts-ignore
    opLogs.value = res.items
     // @ts-ignore
    opPage.total = res.total
  } catch (error) {
    console.error(error)
  } finally {
    opLoading.value = false
  }
}

onMounted(() => {
  fetchLoginLogs()
  fetchOpLogs()
})
</script>

<style scoped>
.logs-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  background-color: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.status-success {
  color: #67c23a;
  font-weight: bold;
}

.status-error {
  color: #f56c6c;
  font-weight: bold;
}
</style>
