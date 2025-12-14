<template>
  <div class="doctor-detail-container" v-loading="loading">
    <el-page-header @back="goBack" title="返回列表">
      <template #content>
        <span class="text-large font-600">医生详情</span>
      </template>
    </el-page-header>
    
    <el-row :gutter="20" class="mt-20">
      <!-- 基本信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="NPI">{{ doctor.npi }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ doctor.full_name }}</el-descriptions-item>
            <el-descriptions-item label="专业">{{ doctor.specialty }}</el-descriptions-item>
            <el-descriptions-item label="州">{{ doctor.state }}</el-descriptions-item>
            <el-descriptions-item label="城市">{{ doctor.city || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <!-- RFM 特征卡片 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>RFM 特征</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="最近互动 (R)">{{ doctor.rfm_recency }}</el-descriptions-item>
            <el-descriptions-item label="互动频次 (F)">{{ doctor.rfm_frequency }}</el-descriptions-item>
            <el-descriptions-item label="总金额 (M)">${{ doctor.rfm_monetary?.toLocaleString() }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      
      <!-- 聚类信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>聚类分组</span>
          </template>
          <div class="cluster-info">
            <el-tag size="large" :type="getClusterTagType(doctor.cluster_id)">
              {{ doctor.cluster_label || `Cluster ${doctor.cluster_id}` }}
            </el-tag>
            <p class="cluster-desc">{{ getClusterDescription(doctor.cluster_id) }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 支付记录 -->
    <el-card shadow="hover" class="mt-20">
      <template #header>
        <span>最近支付记录</span>
      </template>
      <el-table :data="payments" stripe>
        <el-table-column prop="payment_date" label="日期" width="120" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">
            ${{ row.amount?.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="payment_type" label="类型" />
        <el-table-column prop="nature_of_payment" label="性质" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const loading = ref(false)

const doctor = ref<any>({})
const payments = ref<any[]>([])

const fetchDoctorDetail = async () => {
  loading.value = true
  try {
    const npi = route.params.npi as string
    const res: any = await request.get(`/doctors/${npi}`)
    doctor.value = res.doctor || res
    payments.value = res.recent_payments || []
  } catch (error) {
    console.error('Failed to fetch doctor detail:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/doctors')
}

const getClusterTagType = (clusterId: number) => {
  const types = ['success', 'warning', 'info', 'danger']
  return types[clusterId % types.length]
}

const getClusterDescription = (clusterId: number) => {
  const descriptions: Record<number, string> = {
    0: '高价值核心客户，建议重点维护',
    1: '中等价值潜力客户，建议持续跟进',
    2: '大众客户，建议数字化营销覆盖'
  }
  return descriptions[clusterId] || '待分析'
}

onMounted(() => {
  fetchDoctorDetail()
})
</script>

<style scoped>
.doctor-detail-container {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.cluster-info {
  text-align: center;
  padding: 20px 0;
}

.cluster-desc {
  margin-top: 15px;
  color: #666;
}
</style>
