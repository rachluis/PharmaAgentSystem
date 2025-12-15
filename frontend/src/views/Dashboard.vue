<template>
  <div class="dashboard-container">
    <!-- KPI Cards -->
    <div class="kpi-grid">
      <el-card class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea, #764ba2)">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ formatNumber(stats.total_doctors) }}</div>
            <div class="kpi-label">总医生数</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c)">
            <el-icon :size="28"><Money /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">${{ formatNumber(stats.total_monetary, 0) }}</div>
            <div class="kpi-label">总支付金额</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe, #00f2fe)">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">${{ formatNumber(stats.avg_monetary, 0) }}</div>
            <div class="kpi-label">平均金额</div>
          </div>
        </div>
      </el-card>
      
      <el-card class="kpi-card">
        <div class="kpi-content">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #43e97b, #38f9d7)">
            <el-icon :size="28"><DataAnalysis /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ formatNumber(stats.avg_frequency, 1) }}</div>
            <div class="kpi-label">平均频次</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <el-card>
        <template #header>
          <div class="chart-header">
            <span>专业分布 TOP 10</span>
          </div>
        </template>
        <div ref="specialtyChartRef" class="chart-container"></div>
      </el-card>
      
      <el-card>
        <template #header>
          <div class="chart-header">
            <span>州分布 TOP 10</span>
          </div>
        </template>
        <div ref="stateChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <!-- Quick Actions -->
    <div class="actions-grid">
      <el-card class="action-card" @click="$router.push('/doctors')">
        <el-icon :size="40" color="var(--primary)"><User /></el-icon>
        <h3>医生管理</h3>
        <p>查看和筛选医生数据</p>
      </el-card>
      
      <el-card class="action-card" @click="$router.push('/analysis')">
        <el-icon :size="40" color="var(--chart-2)"><DataAnalysis /></el-icon>
        <h3>聚类分析</h3>
        <p>执行 K-Means 客户分群</p>
      </el-card>
      
      <el-card class="action-card" @click="$router.push('/reports')">
        <el-icon :size="40" color="var(--chart-3)"><Document /></el-icon>
        <h3>AI 报告</h3>
        <p>生成智能分析报告</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { User, Money, TrendCharts, DataAnalysis, Document } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import request from '@/api/request'

const stats = reactive({
  total_doctors: 0,
  total_monetary: 0,
  avg_monetary: 0,
  avg_frequency: 0,
  specialty_distribution: {} as Record<string, number>,
  state_distribution: {} as Record<string, number>
})

const specialtyChartRef = ref<HTMLElement>()
const stateChartRef = ref<HTMLElement>()
let specialtyChart: echarts.ECharts | null = null
let stateChart: echarts.ECharts | null = null

const formatNumber = (num: number, decimals = 0) => {
  if (!num) return '0'
  return num.toLocaleString('en-US', { maximumFractionDigits: decimals })
}

const fetchStatistics = async () => {
  try {
    const res: any = await request.get('/doctors/statistics')
    Object.assign(stats, res)
    renderCharts()
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

const renderCharts = () => {
  // Specialty Chart
  if (specialtyChartRef.value) {
    specialtyChart = echarts.init(specialtyChartRef.value)
    const specialtyData = Object.entries(stats.specialty_distribution)
      .map(([name, value]) => ({ name: name.substring(0, 20), value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)
    
    specialtyChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { type: 'scroll', orient: 'vertical', right: 10, top: 20, bottom: 20 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: specialtyData
      }]
    })
  }
  
  // State Chart
  if (stateChartRef.value) {
    stateChart = echarts.init(stateChartRef.value)
    const stateData = Object.entries(stats.state_distribution)
      .sort((a, b) => b[1] - a[1])
    
    stateChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: stateData.map(d => d[0]) },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: stateData.map(d => d[1]),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        barWidth: '60%'
      }]
    })
  }
}

const handleResize = () => {
  specialtyChart?.resize()
  stateChart?.resize()
}

onMounted(() => {
  fetchStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  specialtyChart?.dispose()
  stateChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
  }
}

.kpi-card {
  border-radius: var(--radius-lg);
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.kpi-info {
  flex: 1;
  min-width: 0;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--foreground);
}

.kpi-label {
  font-size: 13px;
  color: var(--muted-foreground);
  margin-top: 4px;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

@media (min-width: 768px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
}

.chart-header {
  font-weight: 600;
  color: var(--foreground);
}

.chart-container {
  height: 350px;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 640px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .actions-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
}

.action-card {
  text-align: center;
  padding: 30px 20px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  border-radius: var(--radius-lg);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.action-card h3 {
  margin: 15px 0 8px;
  color: var(--foreground);
  font-size: 18px;
}

.action-card p {
  color: var(--muted-foreground);
  margin: 0;
  font-size: 14px;
}
</style>

