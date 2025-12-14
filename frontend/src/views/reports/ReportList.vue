<template>
  <div class="report-list-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI 报告列表</span>
          <el-button type="primary" @click="generateReport">
            <el-icon><Plus /></el-icon>
            生成新报告
          </el-button>
        </div>
      </template>
      
      <el-table :data="reports" stripe v-loading="loading">
        <el-table-column prop="report_id" label="ID" width="80" />
        <el-table-column prop="report_title" label="报告标题" min-width="200" />
        <el-table-column prop="report_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getReportTypeName(row.report_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="viewReport(row.report_id)">
              查看
            </el-button>
            <el-button type="danger" size="small" link @click="deleteReport(row.report_id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          :total="pagination.total"
          :page-size="10"
          layout="total, prev, pager, next"
          @current-change="fetchReports"
        />
      </div>
    </el-card>
    
    <!-- 生成报告对话框 -->
    <el-dialog v-model="dialogVisible" title="生成 AI 报告" width="500px">
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="报告类型">
          <el-select v-model="reportForm.report_type" placeholder="选择报告类型">
            <el-option label="聚类分析报告" value="cluster_analysis" />
            <el-option label="医生画像报告" value="doctor_profile" />
            <el-option label="市场策略报告" value="market_strategy" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联聚类">
          <el-select v-model="reportForm.cluster_id" placeholder="选择聚类结果">
            <el-option label="最新聚类结果" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="自定义提示">
          <el-input
            v-model="reportForm.custom_prompt"
            type="textarea"
            rows="3"
            placeholder="请输入您想让AI重点分析的内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGenerateReport" :loading="generating">
          开始生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const loading = ref(false)
const generating = ref(false)
const dialogVisible = ref(false)
const reports = ref<any[]>([])

const pagination = reactive({
  page: 1,
  total: 0
})

const reportForm = reactive({
  report_type: 'cluster_analysis',
  cluster_id: 1,
  custom_prompt: ''
})

const fetchReports = async () => {
  loading.value = true
  try {
    const res: any = await request.get('/reports', {
      params: { page: pagination.page, page_size: 10 }
    })
    reports.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('Failed to fetch reports:', error)
  } finally {
    loading.value = false
  }
}

const generateReport = () => {
  dialogVisible.value = true
}

const submitGenerateReport = async () => {
  generating.value = true
  try {
    const res: any = await request.post('/reports/generate', reportForm)
    ElMessage.success('报告生成任务已创建')
    dialogVisible.value = false
    // Navigate to report detail for streaming view
    if (res.report_id) {
      router.push(`/reports/${res.report_id}`)
    }
  } catch (error) {
    ElMessage.error('生成报告失败')
  } finally {
    generating.value = false
  }
}

const viewReport = (reportId: number) => {
  router.push(`/reports/${reportId}`)
}

const deleteReport = async (reportId: number) => {
  await ElMessageBox.confirm('确定要删除此报告吗？', '提示', {
    type: 'warning'
  })
  try {
    await request.delete(`/reports/${reportId}`)
    ElMessage.success('删除成功')
    fetchReports()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const getReportTypeName = (type: string) => {
  const names: Record<string, string> = {
    cluster_analysis: '聚类分析',
    doctor_profile: '医生画像',
    market_strategy: '市场策略'
  }
  return names[type] || type
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    generating: 'warning',
    published: 'success',
    archived: ''
  }
  return types[status] || ''
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.report-list-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
