<template>
  <div class="analysis-container">
    <el-row :gutter="20">
      <!-- Left: Control Panel -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>聚类配置</span>
            </div>
          </template>
          
          <el-form label-position="top">
            <el-form-item label="聚类数量 (K)">
              <el-slider
                v-model="clusterConfig.k"
                :min="2"
                :max="10"
                :marks="kMarks"
                show-stops
              />
            </el-form-item>
            
            <el-form-item label="特征选择">
              <el-checkbox-group v-model="clusterConfig.features">
                <el-checkbox label="recency_days">R - 最近互动</el-checkbox>
                <el-checkbox label="frequency">F - 互动频次</el-checkbox>
                <el-checkbox label="monetary">M - 总金额</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="analyzing"
                :disabled="clusterConfig.features.length < 2"
                @click="runClustering"
                style="width: 100%"
              >
                <el-icon><DataAnalysis /></el-icon>
                {{ analyzing ? '分析中...' : '开始分析' }}
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-alert
            v-if="analyzing"
            title="正在执行聚类分析..."
            type="info"
            :closable="false"
            show-icon
          >
            <el-progress :percentage="progress" :stroke-width="8" />
          </el-alert>
        </el-card>
        
        <!-- Cluster Summary Cards -->
        <el-card v-if="results.length" shadow="hover" class="mt-20">
          <template #header>
            <span>聚类摘要</span>
          </template>
          <div class="cluster-summary">
            <div
              v-for="cluster in results"
              :key="cluster.cluster_id"
              class="cluster-item"
              :class="{ active: selectedCluster === cluster.cluster_id }"
              @click="selectedCluster = cluster.cluster_id"
            >
              <div class="cluster-header">
                <el-tag :type="getTagType(cluster.cluster_id)">
                  Cluster {{ cluster.cluster_id }}
                </el-tag>
                <span class="cluster-size">{{ cluster.size_count?.toLocaleString() }} 人</span>
              </div>
              <div class="cluster-kpis">
                <div class="kpi">
                  <span class="label">R</span>
                  <span class="value">{{ cluster.kpi_summary?.Avg_R_Days?.toFixed(0) }} 天</span>
                </div>
                <div class="kpi">
                  <span class="label">F</span>
                  <span class="value">{{ cluster.kpi_summary?.Avg_F_Count?.toFixed(1) }}</span>
                </div>
                <div class="kpi">
                  <span class="label">M</span>
                  <span class="value">${{ cluster.kpi_summary?.Avg_M_Amount?.toFixed(0) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- Right: Results -->
      <el-col :span="16">
        <el-card v-if="!results.length" shadow="hover" class="empty-state">
          <el-empty description="请配置参数并开始分析">
            <template #image>
              <el-icon size="100" color="#c0c4cc"><DataAnalysis /></el-icon>
            </template>
          </el-empty>
        </el-card>
        
        <template v-else>
          <!-- Strategy Card -->
          <el-card shadow="hover" class="mb-20">
            <template #header>
              <span>AI 策略建议</span>
            </template>
            <div v-if="selectedClusterData" class="strategy-content">
              <el-tag :type="getTagType(selectedClusterData.cluster_id)" size="large">
                {{ selectedClusterData.cluster_name || `Cluster ${selectedClusterData.cluster_id}` }}
              </el-tag>
              <div class="strategy-text" v-html="formatStrategy(selectedClusterData.strategy_focus)"></div>
            </div>
          </el-card>
          
          <!-- Cluster Table -->
          <el-card shadow="hover">
            <template #header>
              <span>聚类详情</span>
            </template>
            <el-table :data="results" stripe>
              <el-table-column prop="cluster_id" label="ID" width="80" />
              <el-table-column prop="cluster_name" label="名称" width="120">
                <template #default="{ row }">
                  {{ row.cluster_name || `Cluster ${row.cluster_id}` }}
                </template>
              </el-table-column>
              <el-table-column prop="size_count" label="数量">
                <template #default="{ row }">
                  {{ row.size_count?.toLocaleString() }}
                </template>
              </el-table-column>
              <el-table-column prop="size_percentage" label="占比">
                <template #default="{ row }">
                  {{ row.size_percentage?.toFixed(1) }}%
                </template>
              </el-table-column>
              <el-table-column label="平均 R (天)">
                <template #default="{ row }">
                  {{ row.kpi_summary?.Avg_R_Days?.toFixed(0) }}
                </template>
              </el-table-column>
              <el-table-column label="平均 F">
                <template #default="{ row }">
                  {{ row.kpi_summary?.Avg_F_Count?.toFixed(1) }}
                </template>
              </el-table-column>
              <el-table-column label="平均 M ($)">
                <template #default="{ row }">
                  ${{ row.kpi_summary?.Avg_M_Amount?.toFixed(0) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </template>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, DataAnalysis } from '@element-plus/icons-vue'
import request from '@/api/request'

const analyzing = ref(false)
const progress = ref(0)
const selectedCluster = ref(0)
const results = ref<any[]>([])

const clusterConfig = reactive({
  k: 5,
  features: ['recency_days', 'frequency', 'monetary']
})

const kMarks = {
  2: '2',
  5: '5',
  10: '10'
}

const selectedClusterData = computed(() => {
  return results.value.find(c => c.cluster_id === selectedCluster.value)
})

const getTagType = (id: number): '' | 'success' | 'warning' | 'danger' | 'info' => {
  const types: ('' | 'success' | 'warning' | 'danger' | 'info')[] = ['success', 'warning', '', 'danger', 'info']
  return types[id % types.length] || ''
}

const formatStrategy = (text: string) => {
  if (!text) return '<p>暂无策略建议</p>'
  return text.replace(/\n/g, '<br>')
}

const runClustering = async () => {
  if (clusterConfig.features.length < 2) {
    ElMessage.warning('请至少选择2个特征')
    return
  }
  
  analyzing.value = true
  progress.value = 0
  
  // Simulate progress
  const progressInterval = setInterval(() => {
    if (progress.value < 90) {
      progress.value += 10
    }
  }, 500)
  
  try {
    const res: any = await request.post('/analysis/perform', {
      k: clusterConfig.k,
      features: clusterConfig.features
    })
    
    progress.value = 100
    clearInterval(progressInterval)
    
    if (res.clusters) {
      results.value = res.clusters
      selectedCluster.value = 0
      ElMessage.success('聚类分析完成')
    }
  } catch (error) {
    console.error('Clustering failed:', error)
    clearInterval(progressInterval)
  } finally {
    analyzing.value = false
  }
}

const fetchExistingResults = async () => {
  try {
    const res: any = await request.get('/analysis/results')
    if (res && res.length) {
      results.value = res
      selectedCluster.value = 0
    }
  } catch (error) {
    console.log('No existing results')
  }
}

onMounted(() => {
  fetchExistingResults()
})
</script>

<style scoped>
.analysis-container {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.mt-20 {
  margin-top: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}

.cluster-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cluster-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.cluster-item:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.cluster-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.cluster-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.cluster-size {
  font-size: 13px;
  color: #909399;
}

.cluster-kpis {
  display: flex;
  gap: 16px;
}

.kpi {
  display: flex;
  flex-direction: column;
}

.kpi .label {
  font-size: 11px;
  color: #909399;
}

.kpi .value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.strategy-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.strategy-text {
  line-height: 1.8;
  color: #606266;
}
</style>
