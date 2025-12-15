<template>
  <div class="password-strength">
    <div class="strength-bars">
      <div 
        v-for="i in 3" 
        :key="i"
        class="strength-bar"
        :class="getBarClass(i)"
      ></div>
    </div>
    <div class="strength-text" :class="getTextClass()">
      {{ strengthText }}
    </div>
    
    <!-- Optional: Detailed requirements list -->
    <div v-if="showDetails" class="strength-details">
      <div 
        v-for="(req, index) in requirements" 
        :key="index"
        class="requirement-item"
        :class="{ 'met': req.met }"
      >
        <el-icon v-if="req.met" color="var(--success)"><Select /></el-icon>
        <el-icon v-else color="var(--muted-foreground)"><Close /></el-icon>
        <span>{{ req.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Select, Close } from '@element-plus/icons-vue'

const props = defineProps({
  password: {
    type: String,
    default: ''
  },
  showDetails: {
    type: Boolean,
    default: false
  }
})

const requirements = computed(() => {
  const pwd = props.password
  return [
    { label: '至少6个字符', met: pwd.length >= 6 },
    { label: '包含大小写字母', met: /[a-z]/.test(pwd) && /[A-Z]/.test(pwd) },
    { label: '包含数字', met: /\d/.test(pwd) },
    { label: '包含特殊字符', met: /[!@#$%^&*(),.?":{}|<>]/.test(pwd) }
  ]
})

const score = computed(() => {
  if (!props.password) return 0
  return requirements.value.filter(r => r.met).length
})

const strengthText = computed(() => {
  const texts = ['弱', '弱', '中', '强', '强']
  return texts[score.value] || '弱'
})

const getBarClass = (index: number) => {
  const s = score.value
  // Logic: 
  // Score 0-1: 1 bar red
  // Score 2-3: 2 bars orange
  // Score 4: 3 bars green
  
  if (s <= 1) {
    return index === 1 ? 'weak' : ''
  } else if (s <= 3) {
    return index <= 2 ? 'medium' : ''
  } else {
    return 'strong'
  }
}

const getTextClass = () => {
  const s = score.value
  if (s <= 1) return 'text-weak'
  if (s <= 3) return 'text-medium'
  return 'text-strong'
}
</script>

<style scoped>
.password-strength {
  margin-top: 8px;
}

.strength-bars {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}

.strength-bar {
  flex: 1;
  height: 4px;
  background-color: var(--border);
  border-radius: 2px;
  transition: all 0.3s ease;
}

/* Colors using CSS variables or fallbacks */
.strength-bar.weak { background-color: var(--destructive, #f56c6c); }
.strength-bar.medium { background-color: var(--warning, #e6a23c); }
.strength-bar.strong { background-color: var(--success, #67c23a); }

.strength-text {
  font-size: 12px;
  text-align: right;
  margin-bottom: 8px;
  font-weight: 500;
}

.text-weak { color: var(--destructive, #f56c6c); }
.text-medium { color: var(--warning, #e6a23c); }
.text-strong { color: var(--success, #67c23a); }

.strength-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--muted-foreground, #909399);
}

.requirement-item.met {
  color: var(--success, #67c23a);
}
</style>
