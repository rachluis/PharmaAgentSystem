<template>
  <div class="report-detail-container" v-loading="loading">
    <div class="header-actions">
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon> 返回
      </el-button>
      <div class="title-actions">
        <el-tag v-if="report" :type="report.status === 'published' ? 'success' : 'warning'">{{ report.status }}</el-tag>
        <el-button type="danger" plain @click="deleteReport" v-if="report">删除报告</el-button>
      </div>
    </div>

    <el-card v-if="report" class="report-card">
      <template #header>
        <div class="report-header">
          <h1>{{ report.report_title }}</h1>
          <div class="meta-info">
            <span><el-icon><Calendar /></el-icon> {{ new Date(report.created_at).toLocaleString() }}</span>
            <span><el-icon><User /></el-icon> 由 AI 生成</span>
            <span><el-icon><Timer /></el-icon> 耗时 {{ report.generation_time?.toFixed(1) }}s</span>
            <span v-if="report.related_cluster_id" class="link-span" @click="$router.push('/analysis')">
               <el-icon><Connection /></el-icon> 关联聚类 #{{ report.related_cluster_id }}
            </span>
          </div>
        </div>
      </template>

      <div class="markdown-body" v-html="renderedContent"></div>
    </el-card>

    <div v-if="!loading && !report" class="not-found">
      <el-empty description="未找到相关报告" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Calendar, User, Timer, Connection } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { analysisApi } from '@/api/analysis'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const report = ref<any>(null)

const renderedContent = computed(() => {
  if (!report.value || !report.value.report_content) return ''
  return marked(report.value.report_content)
})

const loadReport = async () => {
  const id = Number(route.params.id)
  if (!id) return
  
  loading.value = true
  try {
    const res: any = await analysisApi.getReport(id)
    report.value = res
  } catch (err) {
    console.error(err)
    ElMessage.error('加载报告失败')
  } finally {
    loading.value = false
  }
}

const deleteReport = async () => {
  await ElMessageBox.confirm('确定要删除此报告吗？', '提示', {
    type: 'warning'
  })
  
  try {
    if (report.value?.report_id) {
       await analysisApi.deleteReport(report.value.report_id)
       ElMessage.success('删除成功')
       router.replace('/reports')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-detail-container {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-header h1 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #1f2d3d;
}

.meta-info {
  display: flex;
  gap: 24px;
  color: #909399;
  font-size: 14px;
}

.meta-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.link-span {
  cursor: pointer;
  color: #409eff;
}
.link-span:hover {
  text-decoration: underline;
}

/* Markdown Styles with Theme Support */
.markdown-body {
  font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
  line-height: 1.8;
  color: var(--card-foreground);
  padding: 10px;
}

/* Enhancing markdown styles */
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  padding-bottom: .3em;
  border-bottom: 1px solid var(--border);
  color: var(--card-foreground);
}

.markdown-body :deep(h1) { font-size: 2em; }
.markdown-body :deep(h2) { font-size: 1.5em; }
.markdown-body :deep(h3) { font-size: 1.25em; }

.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-body :deep(li) {
  margin-bottom: 0.5em;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
}

.markdown-body :deep(blockquote) {
  padding: 0 1em;
  color: var(--muted-foreground);
  border-left: 0.25em solid var(--border);
  margin: 0 0 16px 0;
}

.markdown-body :deep(code) {
  padding: .2em .4em;
  margin: 0;
  font-size: 85%;
  background-color: var(--accent);
  color: var(--primary);
  border-radius: 3px;
}

.markdown-body :deep(pre) {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: var(--secondary);
  border-radius: 6px;
  border: 1px solid var(--border);
}

.markdown-body :deep(pre code) {
  background-color: transparent;
  color: var(--secondary-foreground);
  padding: 0;
}
</style>
