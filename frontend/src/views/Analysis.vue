<template>
  <div class="analysis-container">
    <div class="analysis-header">
      <h2>聚类分析</h2>
      <div class="header-actions">
        <el-button type="primary" @click="downloadReport" v-if="results.length > 0">下载各聚类KPI</el-button>
      </div>
    </div>
    
    <div class="analysis-content">
      <!-- Left Sidebar: Configuration -->
      <div class="config-panel">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Setting /></el-icon> 聚类配置</span>
            </div>
          </template>
          
          <el-form label-position="top">
            <el-form-item label="聚类数量 (K)">
              <div class="slider-container">
                <el-slider v-model="kValue" :min="2" :max="10" show-input />
              </div>
            </el-form-item>
            
            <el-form-item label="特征选择">
              <el-checkbox-group v-model="selectedFeatures">
                <div class="feature-item">
                  <el-checkbox label="recency_days" checked>R - 最近互动</el-checkbox>
                </div>
                <div class="feature-item">
                  <el-checkbox label="frequency" checked>F - 互动频次</el-checkbox>
                </div>
                <div class="feature-item">
                  <el-checkbox label="monetary" checked>M - 总金额</el-checkbox>
                </div>
              </el-checkbox-group>
            </el-form-item>
            
            <el-button type="primary" class="run-btn" :loading="analyzing" @click="runAnalysis">
              {{ analyzing ? '分析中...' : '开始分析' }}
            </el-button>
          </el-form>
        </el-card>

        <!-- Only show results list if analysis done -->
        <el-card class="history-card" v-if="results.length > 0">
           <template #header>
            <div class="card-header-row">
              <span>历史结果</span>
            </div>
           </template>
           <el-scrollbar height="300px">
             <div 
               v-for="res in results" 
               :key="res.cluster_id" 
               class="history-item"
               :class="{ active: currentResult?.cluster_id === res.cluster_id }"
               @click="selectResult(res)"
             >
               <span class="history-name">{{ res.cluster_name || `K-Means (K=${res.kpi_summary ? Object.keys(res.kpi_summary).length : '?'})` }}</span>
               <span class="history-date">{{ formatDate(res.task_id) }}</span> 
             </div>
           </el-scrollbar>
        </el-card>
      </div>
      
      <!-- Right Content: Results & Visualization -->
      <div class="results-panel" v-if="currentResult">
        <div class="results-scroll-container">
          <!-- Top: 3D Visualization -->
          <el-card class="viz-card" shadow="hover">
            <template #header>
               <div class="card-header-row">
                  <span>3D 客户分布视图 (R-F-M)</span>
               </div>
            </template>
            <div ref="chartDom" class="chart-container"></div>
          </el-card>
          
          <!-- Middle: Strategy & AI -->
          <div class="strategy-row">
             <el-card class="ai-card" shadow="hover">
                <template #header>
                  <div class="card-header-row">
                    <span><el-icon><MagicStick /></el-icon> AI 策略建议</span>
                    <el-button type="primary" size="small" @click="openAIDialog">生成AI策略</el-button>
                  </div>
                </template>
                
                <div v-if="!currentResult.strategy_focus" class="empty-strategy">
                   暂无策略建议，请点击生成按钮调用 AI 进行分析。
                </div>
                <div v-else class="strategy-content">
                   {{ currentResult.strategy_focus }}
                </div>
             </el-card>
          </div>
          
          <!-- Bottom: Cluster Details Table -->
          <el-card class="table-card" shadow="hover">
             <template #header>
               <div class="card-header-row">
                 <span>聚类详情 KPI</span>
               </div>
             </template>
             <el-table :data="clusterTableData" stripe style="width: 100%">
               <el-table-column prop="cluster_id" label="群组ID" width="80" />
               <el-table-column prop="label" label="群组标签" width="150">
                  <template #default="{ row }">
                     <el-tag>{{ row.label }}</el-tag>
                  </template>
               </el-table-column>
               <el-table-column prop="size" label="人数" width="100">
                 <template #default="{ row }">
                   {{ row.size?.toLocaleString() }}
                 </template>
               </el-table-column>
               <el-table-column prop="size_percentage" label="占比" width="150">
                 <template #default="{ row }">
                   <el-progress :percentage="Number(row.size_percentage?.toFixed(1))" :stroke-width="15" :text-inside="true" />
                 </template>
               </el-table-column>
               <el-table-column label="平均 R (天)">
                 <template #default="{ row }">
                   {{ row.means.recency_days?.toFixed(0) }}
                 </template>
               </el-table-column>
               <el-table-column label="平均 F (次)">
                  <template #default="{ row }">
                    {{ row.means.frequency?.toFixed(1) }}
                  </template>
               </el-table-column>
               <el-table-column label="平均 M ($)">
                  <template #default="{ row }">
                     {{ row.means.monetary?.toLocaleString(undefined, { maximumFractionDigits: 0 }) }}
                  </template>
               </el-table-column>
             </el-table>
          </el-card>
        </div>
      </div>
      
      <!-- Empty State -->
      <div class="empty-results" v-else>
         <el-empty description="请配置参数并开始分析" />
      </div>
    </div>
    
    <!-- AI Dialog -->
    <el-dialog v-model="aiDialogVisible" title="AI 策略生成" width="60%" :close-on-click-modal="false">
      <el-form label-position="top">
        <el-form-item label="自定义关注点 (可选)">
          <el-input 
            v-model="aiUserPrompt" 
            type="textarea" 
            :rows="3" 
            placeholder="例如: 请重点分析高价值客户的流失风险..." 
          />
        </el-form-item>
      </el-form>
      
      <div v-if="aiReportContent" class="ai-report-box">
        <h4>生成结果:</h4>
        <div class="markdown-body" v-html="renderMarkdown(aiReportContent)"></div>
      </div>
      
      <div v-if="aiGenerating" class="generating-indicator">
         <el-icon class="is-loading"><Loading /></el-icon> 正在思考并撰写报告...
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="aiDialogVisible = false">关闭</el-button>
          <el-button type="primary" :disabled="aiGenerating" @click="generateAIStrategy">
            {{ aiGenerating ? '生成中...' : '开始生成' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { Setting, MagicStick, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import 'echarts-gl' // Import GL for 3D charts
import { analysisApi, type ClusterResult } from '@/api/analysis'
import { marked } from 'marked'

// State
const kValue = ref(3)
const selectedFeatures = ref(['recency_days', 'frequency', 'monetary'])
const analyzing = ref(false)
const results = ref<ClusterResult[]>([])
const currentResult = ref<ClusterResult | null>(null)
const chartDom = ref<HTMLElement | null>(null)
let myChart: echarts.ECharts | null = null

// AI Dialog State
const aiDialogVisible = ref(false)
const aiUserPrompt = ref('')
const aiGenerating = ref(false)
const aiReportContent = ref('')

// Computed table data from kpi_summary
const clusterTableData = computed(() => {
   if (!currentResult.value || !currentResult.value.kpi_summary) return []
   
   const summary: any = currentResult.value.kpi_summary
   const labels: any = currentResult.value.cluster_labels || {}
   
   // Convert dictionary { "0": {...}, "1": {...} } to array
   // Ensure we handle both string or parsed object if axios interceptor didn't work (though recent fixes ensure parsing)
   let parsedSummary = summary
   if (typeof summary === 'string') {
      try { parsedSummary = JSON.parse(summary) } catch(e) {}
   }

   let parsedLabels = labels
   if (typeof labels === 'string') {
      try { parsedLabels = JSON.parse(labels) } catch(e) {}
   }
   
   return Object.keys(parsedSummary).map(key => ({
      cluster_id: key,
      label: parsedLabels[key] || `Cluster ${key}`,
      size: parsedSummary[key].count,
      size_percentage: parsedSummary[key].percentage,
      means: parsedSummary[key].means // { recency_days: ..., frequency: ..., monetary: ... }
   }))
})

onMounted(async () => {
  await loadResults()
  window.addEventListener('resize', resizeChart)
})

const loadResults = async () => {
  try {
    const list = await analysisApi.getClusterResults()
    results.value = list
    if (list.length > 0 && list[0]) {
       selectResult(list[0]) // Select latest
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('加载历史结果失败')
  }
}

const selectResult = (res: ClusterResult) => {
   currentResult.value = res
   aiReportContent.value = '' // Clear previous report when switching
   nextTick(() => {
      initChart()
   })
}

const runAnalysis = async () => {
  analyzing.value = true
  try {
    const task = await analysisApi.createTask({
      task_name: `K-Means Analysis (K=${kValue.value})`,
      task_type: 'clustering',
      parameters: {
        k: kValue.value,
        features: selectedFeatures.value
      }
    })
    
    ElMessage.success('分析任务已提交，正在计算...')
    
    // Poll for status
    const poll = setInterval(async () => {
       try {
           const statusRes = await analysisApi.getTask(task.task_id)
           if (statusRes.status === 'completed') {
              clearInterval(poll)
              analyzing.value = false
              ElMessage.success('分析完成！')
              await loadResults() // Reload lists
           } else if (statusRes.status === 'failed') {
              clearInterval(poll)
              analyzing.value = false
              ElMessage.error('分析失败: ' + statusRes.error_message)
           }
       } catch (e) {
           console.error("Polling error", e)
       }
    }, 2000)
    
  } catch (err) {
    analyzing.value = false
    ElMessage.error('启动分析失败')
  }
}

const initChart = () => {
  if (!chartDom.value || !currentResult.value) return
  
  if (myChart) myChart.dispose()
  myChart = echarts.init(chartDom.value)
  
  // Parse visualization data
  let dataPoints = []
  try {
     const rawViz = currentResult.value.visualization_data
     if (typeof rawViz === 'string') {
        dataPoints = JSON.parse(rawViz)
     } else {
        dataPoints = rawViz || []
     }
  } catch (e) {
     console.error("Viz data parse error", e)
     dataPoints = []
  }
  
  // Prepare data for 3D Series
  // We need distinct colors for clusters
  // Colors for visualization categories
  const colorPalette = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4'];
  
  // Prepare valid numerical data
  const seriesData = dataPoints.map((pt: any) => {
     return [
        pt['recency_days'],
        pt['frequency'],
        pt['monetary'],
        pt.cluster // 4th dimension for color
     ]
  });

  const option = {
    tooltip: {},
    visualMap: {
      show: true,
      dimension: 3, // Cluster ID
      categories: Array.from(new Set(dataPoints.map((p: any) => p.cluster))),
      inRange: {
        color: colorPalette
      },
      textStyle: { color: '#333' }
    },
    xAxis3D: { name: 'Recency (R)', type: 'value', nameTextStyle: { fontSize: 14 } },
    yAxis3D: { name: 'Frequency (F)', type: 'value', nameTextStyle: { fontSize: 14 } },
    zAxis3D: { name: 'Monetary (M)', type: 'value', nameTextStyle: { fontSize: 14 } },
    grid3D: {
      viewControl: {
        projection: 'perspective',
        autoRotate: true,
        autoRotateSpeed: 5
      },
      boxWidth: 200,
      boxDepth: 200,
      light: {
          main: {
              intensity: 1.2,
              shadow: true
          },
          ambient: {
              intensity: 0.3
          }
      }
    },
    series: [
      {
        type: 'scatter3D',
        data: seriesData,
        symbolSize: 6,
        itemStyle: {
           opacity: 0.8,
           borderWidth: 0.5,
           borderColor: '#fff' 
        },
        emphasis: {
            label: {
                show: false
            },
            itemStyle: {
                color: 'red',
                borderWidth: 1
            }
        }
      }
    ]
  }
  
  myChart.setOption(option)
}

const resizeChart = () => {
   myChart?.resize()
}

// AI Functions
const openAIDialog = () => {
   aiDialogVisible.value = true
}

const generateAIStrategy = async () => {
  if (!currentResult.value) return
  
  aiGenerating.value = true
  aiReportContent.value = '' // Start fresh
  
  try {
    // Generate streaming
    await analysisApi.generateStrategyStream(
       currentResult.value.cluster_id,
       aiUserPrompt.value,
       (chunk: string) => {
          aiReportContent.value += chunk
       },
       (error: Error) => {
          console.error(error)
          ElMessage.error('生成中断')
          aiGenerating.value = false
       },
       async () => {
          aiGenerating.value = false
          ElMessage.success('生成完成')
          // Refresh results to get the saved strategy from DB
          const currentId = currentResult.value?.cluster_id
          await loadResults()
          if (currentId) {
             const found = results.value.find(r => r.cluster_id === currentId)
             if (found) {
                selectResult(found)
             }
          }
       }
    )
  } catch (e) {
     aiGenerating.value = false
     ElMessage.error('请求失败')
  }
}

// Simple markdown renderer
const renderMarkdown = (text: string) => {
   return marked.parse(text)
}

const formatDate = (id: number) => {
   return `Task #${id}`
}

// Helper to escape CSV values
const escapeCsv = (val: any) => {
   if (val === null || val === undefined) return ''
   const str = String(val)
   if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`
   }
   return str
}

const downloadReport = () => {
   if (!clusterTableData.value || clusterTableData.value.length === 0) {
      ElMessage.warning('暂无数据可下载')
      return
   }

   // define csv headers
   const headers = ['ClusterID', 'Label', 'Size', 'Percentage(%)', 'Avg_Recency_Days', 'Avg_Frequency', 'Avg_Monetary']
   
   // map data to rows
   const rows = clusterTableData.value.map(row => [
      row.cluster_id,
      row.label,
      row.size,
      row.size_percentage,
      row.means.recency_days?.toFixed(2),
      row.means.frequency?.toFixed(2),
      row.means.monetary?.toFixed(2)
   ])

   // Construct CSV content with BOM for Excel utf-8 compatibility
   const csvContent = '\uFEFF' + 
      headers.join(',') + '\n' + 
      rows.map(r => r.map(escapeCsv).join(',')).join('\n')
   
   // Create blob and triggering download
   const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
   const url = URL.createObjectURL(blob)
   const link = document.createElement('a')
   link.href = url
   link.setAttribute('download', `cluster_report_${kValue.value}_groups.csv`)
   document.body.appendChild(link)
   link.click()
   document.body.removeChild(link)
}
</script>

<style scoped>
.analysis-container {
  padding: 24px;
  height: calc(100vh - 64px); /* Optimized for typical topbar height */
  display: flex;
  flex-direction: column;
  background-color: #f6f8fb; /* Light pleasant background */
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.analysis-header h2 {
   font-weight: 600;
   color: #1f2d3d;
   margin: 0;
}

.analysis-content {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0; 
}

/* Sidebar */
.config-panel {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex-shrink: 0;
}

.config-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.card-header {
   font-weight: 600;
   font-size: 16px;
   display: flex;
   align-items: center;
   gap: 8px;
}

.slider-container {
  padding: 0 10px;
}

.feature-item {
  margin-bottom: 12px;
}

.run-btn {
  width: 100%;
  margin-top: 24px;
  height: 40px;
  font-size: 16px;
  border-radius: 6px;
}

.history-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; 
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.history-list-content {
  padding: 10px 0;
}

.history-item {
  padding: 16px;
  border-bottom: 1px solid #f0f2f5;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s;
  border-radius: 6px;
  margin: 0 10px 8px;
  background: white;
}

.history-item:hover {
  background: #f9fafc;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.history-item.active {
  background: #ecf5ff;
  border-left: 4px solid #409eff;
}

.history-name {
  font-weight: 600;
  color: #303133;
}

.history-date {
  color: #909399;
  font-size: 12px;
}

/* Right Content */
.results-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden; /* Prevent body scroll */
  padding-right: 4px; /* for scrollbar */
}

/* Internal scroll container for results */
.results-scroll-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  padding-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Cards style */
.viz-card, .ai-card, .table-card {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.2s;
  min-height: 650px; /* Unified large height */
  display: flex;
  flex-direction: column;
}

.viz-card:hover, .ai-card:hover, .table-card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.08);
}

.chart-container {
  height: 400px;
  width: 100%;
}

.strategy-row {
  margin-bottom: 0;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.strategy-content {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap; /* preserve formatting */
}

.empty-strategy {
  color: #C0C4CC;
  text-align: center;
  padding: 30px;
  background: #fafafa;
  border-radius: 4px;
  font-style: italic;
}

/* AI Report Dialog */
.ai-report-box {
  margin-top: 20px;
  padding: 24px;
  background: #fcfcfc;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  max-height: 400px;
  overflow-y: auto;
  box-shadow: inset 0 0 8px rgba(0,0,0,0.02);
}

.generating-indicator {
  margin-top: 15px;
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  padding: 10px;
  background: #ecf5ff;
  border-radius: 4px;
}

/* Markdown Styles */
.markdown-body {
  font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif;
  line-height: 1.7;
  color: #2c3e50;
}
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}
.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 16px;
}
.markdown-body :deep(p) {
  margin-bottom: 16px;
}
.markdown-body :deep(strong) {
  color: #409eff;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent; 
}
::-webkit-scrollbar-thumb {
  background: #dcdfe6; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc; 
}
</style>
