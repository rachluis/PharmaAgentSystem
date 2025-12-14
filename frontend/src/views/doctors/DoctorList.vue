<template>
  <div class="doctor-list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>医生列表</span>
          <el-button type="primary" size="small" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </template>
      
      <!-- 筛选栏 -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="专业">
          <el-select v-model="filterForm.specialty" placeholder="选择专业" clearable filterable>
            <el-option
              v-for="spec in specialtyOptions"
              :key="spec"
              :label="spec"
              :value="spec"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="州">
          <el-select v-model="filterForm.state" placeholder="选择州" clearable>
            <el-option
              v-for="state in stateOptions"
              :key="state"
              :label="state"
              :value="state"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="聚类">
          <el-select v-model="filterForm.clusterId" placeholder="选择聚类" clearable>
            <el-option label="Cluster 0 - 核心客户" :value="0" />
            <el-option label="Cluster 1 - 大众客户" :value="1" />
            <el-option label="Cluster 2 - 潜力客户" :value="2" />
            <el-option label="Cluster 3 - 普通客户" :value="3" />
            <el-option label="Cluster 4 - 低价值客户" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 数据表格 -->
      <div class="table-wrapper" style="height: 500px; overflow-y: auto;">
        <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
          <el-table-column prop="npi" label="NPI" width="120" />
          <el-table-column label="姓名" width="180">
            <template #default="{ row }">
              {{ row.full_name || `${row.first_name || ''} ${row.last_name || ''}`.trim() }}
            </template>
          </el-table-column>
          <el-table-column prop="specialty" label="专业" width="180">
            <template #default="{ row }">
              <span class="clickable" @click="applyFilter('specialty', row.specialty)">{{ row.specialty }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="state" label="州" width="80">
            <template #default="{ row }">
              <span class="clickable" @click="applyFilter('state', row.state)">{{ row.state }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="rfm_monetary" label="总金额 ($)" width="120">
            <template #default="{ row }">
              {{ formatMoney(row.rfm_monetary) }}
            </template>
          </el-table-column>
          <el-table-column prop="rfm_frequency" label="频次" width="80" />
          <el-table-column prop="cluster_label" label="分群" width="100">
            <template #default="{ row }">
              <el-tag :type="getClusterTagType(row.cluster_id)">
                {{ row.cluster_label || `Cluster ${row.cluster_id}` }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" link @click="viewDetail(row.npi)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const specialtyOptions = ref<string[]>([])
const stateOptions = ref<string[]>([])

const filterForm = reactive({
  specialty: '',
  state: '',
  clusterId: null as number | null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 获取筛选器选项
const fetchFilterOptions = async () => {
  try {
    const [specialtiesRes, statesRes]: any[] = await Promise.all([
      request.get('/doctors/specialties'),
      request.get('/doctors/states')
    ])
    specialtyOptions.value = specialtiesRes.specialties || []
    stateOptions.value = statesRes.states || []
  } catch (error) {
    console.error('Failed to fetch filter options:', error)
  }
}

// 获取医生列表
const fetchDoctors = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterForm.specialty) params.specialty = filterForm.specialty
    if (filterForm.state) params.state = filterForm.state
    if (filterForm.clusterId !== null) params.cluster_id = filterForm.clusterId
    
    const res: any = await request.get('/doctors', { params })
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('Failed to fetch doctors:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchDoctors()
}

const handleReset = () => {
  filterForm.specialty = ''
  filterForm.state = ''
  filterForm.clusterId = null
  pagination.page = 1
  fetchDoctors()
}

const handleSizeChange = () => {
  fetchDoctors()
}

const handlePageChange = () => {
  fetchDoctors()
}

const viewDetail = (npi: string) => {
  router.push(`/doctors/${npi}`)
}

const formatMoney = (value: number) => {
  return value ? `$${value.toLocaleString()}` : '-'
}

const getClusterTagType = (clusterId: number) => {
  const types = ['success', 'warning', 'info', 'danger']
  return types[clusterId % types.length]
}

// Apply quick filter from table clicks
const applyFilter = (field: string, value: string) => {
  if (field === 'specialty') {
    filterForm.specialty = value
  } else if (field === 'state') {
    filterForm.state = value
  }
  handleSearch()
}

const handleExport = () => {
  try {
    // 准备CSV数据
    const headers = ['NPI', '姓名', '专业', '州', '总金额', '频次', '分群']
    const csvData = [headers.join(',')]
    
    tableData.value.forEach((row: any) => {
      const rowData = [
        row.npi || '',
        `"${(row.first_name || '') + ' ' + (row.last_name || '')}"`,
        `"${row.specialty || ''}"`,
        row.state || '',
        row.monetary || 0,
        row.frequency || 0,
        row.cluster_label || `Cluster ${row.cluster_id || 0}`
      ]
      csvData.push(rowData.join(','))
    })
    
    // 创建Blob并下载
    const blob = new Blob(['\ufeff' + csvData.join('\n')], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `doctors_${Date.now()}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  fetchFilterOptions()
  fetchDoctors()
})
</script>

<style scoped>
.doctor-list-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.clickable {
  cursor: pointer;
  color: #409EFF;
}

</style>
