<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Total Doctors</span>
            </div>
          </template>
          <div class="metric">738,772</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Avg Monetary</span>
            </div>
          </template>
          <div class="metric">$3,377</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="chart-card" shadow="hover">
      <h3>Analysis Overview</h3>
      <div
        style="
          height: 300px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #999;
        "
      >
        Chart Placeholder
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.metric {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
.chart-card {
  margin-top: 20px;
}
</style>
