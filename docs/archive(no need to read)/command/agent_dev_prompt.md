# 医药市场智能分析系统 - Agent开发总提示词

> **目标**：指导AI Agent开发一个完整的基于LLM智能体的医药市场分析系统
> **技术栈**：FastAPI + Vue3 + SQLite + Dify + K-Means
> **开发模式**：模块化开发，前后端分离，迭代交付

---

## 🎯 项目概述

你是一个资深全栈开发工程师，负责开发一个医药市场智能分析系统。该系统的核心功能是：

1. **用户认证与权限管理**：支持注册、登录、角色权限
2. **医生数据管理**：查询、筛选、统计738,772名医生的RFM数据
3. **K-Means聚类分析**：自动将医生分群，生成可视化图表
4. **AI智能报告生成**：通过Dify工作流，自动生成市场策略报告
5. **数据看板**：展示关键业务指标和趋势

## 📋 开发原则

### 原则1：代码质量优先

- 每个函数/组件都要有清晰的类型注解（Python/TypeScript）
- 遵循RESTful API设计规范
- 错误处理要完善，给出明确的错误提示
- 代码注释要详细，特别是复杂逻辑部分

### 原则2：用户体验至上

- 所有操作要有Loading状态
- 数据加载失败要有友好的错误页面
- 使用动画增强交互体验（但不要过度）
- 移动端要响应式适配

### 原则3：性能优化

- 列表查询要支持分页和懒加载
- 图表数据要按需加载，避免一次性传输大量数据
- 使用虚拟滚动处理大列表
- 静态资源要CDN加速

### 原则4：安全性

- 密码要用bcrypt加密存储
- JWT Token要设置合理的过期时间
- API要有权限校验
- 防止SQL注入和XSS攻击

---

## 🔧 技术实现指南

### 第一部分：后端开发 (FastAPI)

#### 1.1 项目初始化

**任务**：搭建FastAPI项目骨架

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install fastapi uvicorn sqlalchemy pydantic bcrypt python-jose pandas scikit-learn httpx
```

**目录结构**：

```
backend/
├── app/
│   ├── main.py              # 入口文件
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── models/              # SQLAlchemy模型
│   ├── schemas/             # Pydantic模型
│   ├── routers/             # API路由
│   ├── services/            # 业务逻辑
│   ├── core/                # 核心模块（安全、异常）
│   └── dify_tools/          # Dify工具
├── scripts/                 # 脚本
└── pharma.db                # 数据库文件
```

#### 1.2 数据库模型定义

**任务**：创建7张核心表的SQLAlchemy模型

**关键代码示例**：

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
  
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="viewer")  # admin/analyst/viewer
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
```

**要实现的模型**：

1. `User` - 用户表
2. `Doctor` - 医生表（扩展现有字段）
3. `PaymentRecord` - 支付记录表
4. `AnalysisTask` - 分析任务表
5. `ClusterResult` - 聚类结果表
6. `AIReport` - AI报告表
7. `SystemLog` - 系统日志表

#### 1.3 认证系统实现

**任务**：实现JWT Token认证

**关键步骤**：

1. 创建 `app/core/security.py`：

   - `get_password_hash()` - bcrypt密码哈希
   - `verify_password()` - 验证密码
   - `create_access_token()` - 生成JWT
   - `get_current_user()` - 验证并获取当前用户
2. 创建 `app/routers/auth.py`：

   - `POST /api/v1/auth/register` - 注册
   - `POST /api/v1/auth/login` - 登录
   - `GET /api/v1/auth/me` - 获取当前用户信息
   - `POST /api/v1/auth/logout` - 登出

**示例代码**：

```python
# app/core/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 1.4 医生数据API

**任务**：实现医生数据的CRUD接口

**API列表**：

```python
# app/routers/doctors.py
@router.get("/doctors")
async def get_doctors(
    page: int = 1,
    page_size: int = 20,
    specialty: Optional[str] = None,
    state: Optional[str] = None,
    cluster_id: Optional[int] = None,
    min_monetary: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """分页查询医生列表，支持多条件筛选"""
    # 构建查询
    query = db.query(Doctor)
  
    if specialty:
        query = query.filter(Doctor.specialty == specialty)
    if state:
        query = query.filter(Doctor.state == state)
    if cluster_id is not None:
        query = query.filter(Doctor.cluster_id == cluster_id)
    if min_monetary:
        query = query.filter(Doctor.rfm_monetary >= min_monetary)
  
    # 分页
    total = query.count()
    doctors = query.offset((page - 1) * page_size).limit(page_size).all()
  
    return {
        "code": 200,
        "data": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": doctors
        }
    }

@router.get("/doctors/{npi}")
async def get_doctor_detail(npi: str, db: Session = Depends(get_db)):
    """获取医生详情，包括支付历史"""
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
  
    # 获取最近10条支付记录
    payments = db.query(PaymentRecord)\
        .filter(PaymentRecord.npi == npi)\
        .order_by(PaymentRecord.payment_date.desc())\
        .limit(10)\
        .all()
  
    return {
        "code": 200,
        "data": {
            "doctor": doctor,
            "recent_payments": payments
        }
    }

@router.get("/doctors/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """获取医生数据统计"""
    total_doctors = db.query(Doctor).count()
    total_monetary = db.query(func.sum(Doctor.rfm_monetary)).scalar()
    avg_monetary = db.query(func.avg(Doctor.rfm_monetary)).scalar()
  
    # 专业分布
    specialty_dist = db.query(
        Doctor.specialty, 
        func.count(Doctor.npi)
    ).group_by(Doctor.specialty).all()
  
    return {
        "code": 200,
        "data": {
            "total_doctors": total_doctors,
            "total_monetary": float(total_monetary),
            "avg_monetary": float(avg_monetary),
            "specialty_distribution": dict(specialty_dist)
        }
    }
```

#### 1.5 K-Means聚类服务

**任务**：封装K-Means算法为服务

**关键代码**：

```python
# app/services/analysis_service.py
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import json

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
  
    def perform_clustering(self, k: int = 3, features: list = None):
        """执行K-Means聚类"""
        # 1. 从数据库加载数据
        doctors = self.db.query(Doctor).all()
        df = pd.DataFrame([{
            'npi': d.npi,
            'rfm_frequency': d.rfm_frequency,
            'rfm_monetary': d.rfm_monetary
        } for d in doctors])
      
        # 2. 特征标准化
        if features is None:
            features = ['rfm_frequency', 'rfm_monetary']
      
        X = df[features].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
      
        # 3. 执行聚类
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
      
        # 4. 计算评估指标
        silhouette = silhouette_score(X_scaled, labels)
        inertia = kmeans.inertia_
      
        # 5. 计算每个聚类的统计信息
        df['cluster'] = labels
        cluster_stats = {}
      
        for cluster_id in range(k):
            cluster_df = df[df['cluster'] == cluster_id]
            cluster_stats[str(cluster_id)] = {
                'size': len(cluster_df),
                'avg_frequency': float(cluster_df['rfm_frequency'].mean()),
                'avg_monetary': float(cluster_df['rfm_monetary'].mean()),
                'label': self._generate_cluster_label(cluster_df)
            }
      
        # 6. 保存聚类结果到数据库
        cluster_result = ClusterResult(
            k_value=k,
            algorithm='k-means',
            features_used=json.dumps(features),
            cluster_stats=json.dumps(cluster_stats),
            silhouette_score=silhouette,
            inertia=inertia,
            is_active=True
        )
      
        # 7. 更新医生表的cluster_id
        for _, row in df.iterrows():
            self.db.query(Doctor)\
                .filter(Doctor.npi == row['npi'])\
                .update({'cluster_id': int(row['cluster'])})
      
        self.db.add(cluster_result)
        self.db.commit()
      
        return cluster_result
  
    def _generate_cluster_label(self, cluster_df):
        """根据特征自动生成聚类标签"""
        avg_monetary = cluster_df['rfm_monetary'].mean()
        avg_frequency = cluster_df['rfm_frequency'].mean()
      
        if avg_monetary > 10000 and avg_frequency > 20:
            return "顶级客户"
        elif avg_monetary > 5000:
            return "核心客户"
        elif avg_monetary > 1000:
            return "潜力客户"
        else:
            return "大众客户"
```

#### 1.6 Dify集成服务

**任务**：创建Dify服务，实现AI报告生成

**关键代码**：

```python
# app/services/dify_service.py
import httpx
from typing import AsyncGenerator
import os

class DifyService:
    def __init__(self):
        self.base_url = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
        self.api_key = os.getenv("DIFY_API_KEY")
        self.workflow_id = os.getenv("DIFY_WORKFLOW_ID")
  
    async def generate_report_stream(
        self, 
        user_input: str,
        cluster_data: dict,
        user_id: int
    ) -> AsyncGenerator[str, None]:
        """流式生成报告"""
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/workflows/run",
                json={
                    "inputs": {
                        "user_query": user_input,
                        "cluster_stats": cluster_data,
                        "user_context": f"analyst_{user_id}"
                    },
                    "response_mode": "streaming",
                    "user": f"user_{user_id}"
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        if data == "[DONE]":
                            break
                        yield data + "\n"
```

**报告生成API**：

```python
# app/routers/reports.py
from fastapi.responses import StreamingResponse

@router.post("/reports/generate")
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成AI报告（异步）"""
    # 1. 创建报告记录
    report = AIReport(
        report_title=request.title or "AI分析报告",
        report_type=request.report_type,
        related_cluster_id=request.cluster_id,
        generated_by=current_user.id,
        status="generating"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
  
    # 2. 获取聚类数据
    cluster = db.query(ClusterResult)\
        .filter(ClusterResult.cluster_id == request.cluster_id)\
        .first()
  
    cluster_data = json.loads(cluster.cluster_stats)
  
    # 3. 返回报告ID，前端通过stream接口获取内容
    return {
        "code": 200,
        "data": {
            "report_id": report.report_id,
            "status": "generating",
            "stream_url": f"/api/v1/reports/{report.report_id}/stream"
        }
    }

@router.get("/reports/{report_id}/stream")
async def stream_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """SSE流式输出报告内容"""
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404)
  
    dify_service = DifyService()
  
    async def event_generator():
        full_content = ""
        async for chunk in dify_service.generate_report_stream(
            user_input=report.report_title,
            cluster_data={},  # 从数据库获取
            user_id=report.generated_by
        ):
            full_content += chunk
            yield f"data: {chunk}\n\n"
      
        # 保存完整报告
        report.report_content = full_content
        report.status = "published"
        db.commit()
      
        yield "data: [DONE]\n\n"
  
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

### 第二部分：前端开发 (Vue3 + TypeScript)

#### 2.1 项目初始化

**任务**：使用Vite创建Vue3项目

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install

# 安装依赖
npm install vue-router@4 pinia axios element-plus
npm install echarts vue-echarts
npm install @vueuse/core dayjs markdown-it
npm install sass -D
```

**配置Vite代理**：

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

#### 2.2 Axios封装

**任务**：封装HTTP请求，统一处理错误和Token

```typescript
// src/utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const { code, message, data } = response.data
  
    if (code === 200) {
      return data
    } else {
      ElMessage.error(message || '请求失败')
      return Promise.reject(new Error(message))
    }
  },
  error => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
```

#### 2.3 API模块

**任务**：封装所有API调用

```typescript
// src/api/auth.ts
import request from '@/utils/request'

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
  full_name?: string
}

export const authAPI = {
  // 登录
  login(data: LoginForm) {
    return request.post('/auth/login', data)
  },
  
  // 注册
  register(data: RegisterForm) {
    return request.post('/auth/register', data)
  },
  
  // 获取当前用户信息
  getCurrentUser() {
    return request.get('/auth/me')
  },
  
  // 登出
  logout() {
    return request.post('/auth/logout')
  }
}

// src/api/doctor.ts
export interface DoctorQuery {
  page?: number
  page_size?: number
  specialty?: string
  state?: string
  cluster_id?: number
}

export const doctorAPI = {
  // 获取医生列表
  getDoctors(params: DoctorQuery) {
    return request.get('/doctors', { params })
  },
  
  // 获取医生详情
  getDoctorDetail(npi: string) {
    return request.get(`/doctors/${npi}`)
  },
  
  // 获取统计数据
  getStatistics() {
    return request.get('/doctors/statistics')
  }
}

// src/api/analysis.ts
export interface ClusteringRequest {
  k: number
  features?: string[]
  task_name: string
}

export const analysisAPI = {
  // 执行聚类
  performClustering(data: ClusteringRequest) {
    return request.post('/analysis/clustering/perform', data)
  },
  
  // 获取聚类结果
  getClusterResults(clusterId: number) {
    return request.get(`/analysis/clustering/results/${clusterId}`)
  },
  
  // 获取任务状态
  getTaskStatus(taskId: number) {
    return request.get(`/analysis/tasks/${taskId}/status`)
  }
}

// src/api/report.ts
export const reportAPI = {
  // 生成报告
  generateReport(data: {
    report_type: string
    cluster_id: number
    custom_prompt?: string
  }) {
    return request.post('/reports/generate', data)
  },
  
  // 获取报告列表
  getReports(params: {
    page?: number
    page_size?: number
    report_type?: string
  }) {
    return request.get('/reports', { params })
  },
  
  // 获取报告详情
  getReportDetail(reportId: number) {
    return request.get(`/reports/${reportId}`)
  }
}
```

#### 2.4 Pinia状态管理

**任务**：创建用户、分析、报告等状态

```typescript
// src/store/user.ts
import { defineStore } from 'pinia'
import { authAPI } from '@/api/auth'

interface User {
  id: number
  username: string
  email: string
  role: string
  avatar_url: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as User | null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },
  
  actions: {
    async login(username: string, password: string) {
      const data = await authAPI.login({ username, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
    },
  
    async fetchUserInfo() {
      const data = await authAPI.getCurrentUser()
      this.user = data
    },
  
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})

// src/store/analysis.ts
export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    currentTask: null,
    clusterResults: null,
    isAnalyzing: false
  }),
  
  actions: {
    async startClustering(k: number, features: string[]) {
      this.isAnalyzing = true
      try {
        const data = await analysisAPI.performClustering({
          k,
          features,
          task_name: `K=${k}聚类分析`
        })
        this.currentTask = data
      
        // 轮询任务状态
        return await this.pollTaskStatus(data.task_id)
      } finally {
        this.isAnalyzing = false
      }
    },
  
    async pollTaskStatus(taskId: number) {
      const poll = async () => {
        const data = await analysisAPI.getTaskStatus(taskId)
        if (data.status === 'completed') {
          this.clusterResults = await analysisAPI.getClusterResults(data.result_id)
          return this.clusterResults
        } else if (data.status === 'failed') {
          throw new Error(data.error_message)
        } else {
          await new Promise(resolve => setTimeout(resolve, 2000))
          return poll()
        }
      }
      return poll()
    }
  }
})
```

#### 2.5 核心页面开发

##### 2.5.1 登录页

```vue
<!-- src/views/auth/LoginView.vue -->
<template>
  <div class="login-container">
    <div class="login-left">
      <div class="brand">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
        <h1>医药市场智能分析系统</h1>
        <p class="slogan">数据驱动决策，智能赋能医疗</p>
      </div>
    
      <!-- 动态背景动画 -->
      <div class="bg-animation">
        <div class="particle" v-for="i in 20" :key="i"></div>
      </div>
    </div>
  
    <div class="login-right">
      <el-card class="login-card">
        <h2>用户登录</h2>
      
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
        
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
        
          <el-form-item>
            <el-checkbox v-model="form.remember">记住我</el-checkbox>
          </el-form-item>
        
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              native-type="submit"
              class="login-btn"
            >
              登录
            </el-button>
          </el-form-item>
        
          <div class="footer-links">
            <router-link to="/register">没有账号？立即注册</router-link>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const loading = ref(false)
const formRef = ref()

const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  height: 100vh;
  
  .login-left {
    flex: 1;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  
    .brand {
      position: relative;
      z-index: 2;
      text-align: center;
    
      .logo {
        width: 120px;
        margin-bottom: 24px;
      }
    
      h1 {
        font-size: 32px;
        margin-bottom: 16px;
      }
    
      .slogan {
        font-size: 18px;
        opacity: 0.9;
      }
    }
  
    .bg-animation {
      position: absolute;
      inset: 0;
      overflow: hidden;
    
      .particle {
        position: absolute;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 20s infinite;
      
        @for $i from 1 through 20 {
          &:nth-child(#{$i}) {
            width: random(60) + 20px;
            height: random(60) + 20px;
            left: random(100) * 1%;
            top: random(100) * 1%;
            animation-delay: random(20) * 0.1s;
          }
        }
      }
    }
  }
  
  .login-right {
    width: 480px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
  
    .login-card {
      width: 360px;
    
      h2 {
        text-align: center;
        margin-bottom: 32px;
        color: $text-primary;
      }
    
      .login-btn {
        width: 100%;
      }
    
      .footer-links {
        text-align: center;
        margin-top: 16px;
      
        a {
          color: $primary-color;
          text-decoration: none;
        
          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}
</style>
```

##### 2.5.2 Dashboard

```vue
<!-- src/views/dashboard/DashboardView.vue -->
<template>
  <div class="dashboard">
    <!-- KPI卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :xs="24" :sm="12" :md="6" v-for="kpi in kpis" :key="kpi.title">
        <DataCard
          :title="kpi.title"
          :main-value="kpi.value"
          :trend="kpi.trend"
          :label="kpi.label"
          :icon="kpi.icon"
          :icon-color="kpi.color"
        />
      </el-col>
    </el-row>
  
    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :md="12">
        <el-card title="专业分布">
          <PieChart :data="specialtyData" />
        </el-card>
      </el-col>
    
      <el-col :xs="24" :md="12">
        <el-card title="月度趋势">
          <LineChart :data="trendData" />
        </el-card>
      </el-col>
    </el-row>
  
    <!-- 快速操作 -->
    <el-row class="action-row">
      <el-button type="primary" size="large" @click="startAnalysis">
        <el-icon><DataAnalysis /></el-icon>
        开始新分析
      </el-button>
      <el-button size="large" @click="viewReports">
        <el-icon><Document /></el-icon>
        查看报告
      </el-button>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { doctorAPI } from '@/api/doctor'
import DataCard from '@/components/common/DataCard.vue'
import PieChart from '@/components/charts/PieChart.vue'
import LineChart from '@/components/charts/LineChart.vue'

const router = useRouter()

const kpis = ref([
  {
    title: '总医生数',
    value: '738,772',
    trend: 2.3,
    label: '较上月',
    icon: 'User',
    color: '#1890FF'
  },
  {
    title: '总金额',
    value: '$2.50B',
    trend: 5.1,
    label: '较上月',
    icon: 'Money',
    color: '#52C41A'
  },
  {
    title: '平均金额',
    value: '$3,377',
    trend: 1.8,
    label: '较上月',
    icon: 'TrendCharts',
    color: '#FAAD14'
  },
  {
    title: '最近分析',
    value: '2小时前',
    trend: 0,
    label: 'K=3聚类',
    icon: 'Clock',
    color: '#13C2C2'
  }
])

const specialtyData = ref([])
const trendData = ref([])

onMounted(async () => {
  const stats = await doctorAPI.getStatistics()
  // 处理数据...
})

const startAnalysis = () => {
  router.push('/analysis')
}

const viewReports = () => {
  router.push('/reports')
}
</script>
```

##### 2.5.3 聚类分析页

```vue
<!-- src/views/analysis/ClusterAnalysisView.vue -->
<template>
  <div class="analysis-view">
    <el-row :gutter="16">
      <!-- 左侧配置面板 -->
      <el-col :xs="24" :md="6">
        <el-card title="聚类配置">
          <el-form :model="config" label-width="80px">
            <el-form-item label="K值">
              <el-slider
                v-model="config.k"
                :min="2"
                :max="10"
                :marks="{ 2: '2', 3: '3', 5: '5', 10: '10' }"
                show-stops
              />
            </el-form-item>
          
            <el-form-item label="特征选择">
              <el-checkbox-group v-model="config.features">
                <el-checkbox label="rfm_frequency">频次</el-checkbox>
                <el-checkbox label="rfm_monetary">金额</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          
            <el-form-item>
              <el-button
                type="primary"
                :loading="analysisStore.isAnalyzing"
                @click="handleStartAnalysis"
                block
              >
                {{ analysisStore.isAnalyzing ? '分析中...' : '开始分析' }}
              </el-button>
            
              <el-button @click="viewHistory" block>查看历史</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    
      <!-- 右侧结果展示 -->
      <el-col :xs="24" :md="18">
        <!-- 分析中状态 -->
        <div v-if="analysisStore.isAnalyzing" class="analyzing">
          <el-progress
            :percentage="progress"
            :format="() => `分析进度: ${progress}%`"
          />
          <p class="tip">正在执行K-Means聚类算法...</p>
        </div>
      
        <!-- 结果展示 -->
        <div v-else-if="analysisStore.clusterResults">
          <!-- 评估指标 -->
          <el-row :gutter="16" class="metrics-row">
            <el-col :span="12">
              <el-statistic
                title="轮廓系数"
                :value="analysisStore.clusterResults.silhouette_score"
                :precision="3"
              />
            </el-col>
            <el-col :span="12">
              <el-statistic
                title="惯性"
                :value="analysisStore.clusterResults.inertia"
                :precision="2"
              />
            </el-col>
          </el-row>
        
          <!-- 图表 -->
          <el-tabs v-model="activeTab">
            <el-tab-pane label="3D散点图" name="scatter">
              <ScatterChart3D :data="scatterData" />
            </el-tab-pane>
          
            <el-tab-pane label="雷达图" name="radar">
              <RadarChart :data="radarData" />
            </el-tab-pane>
          
            <el-tab-pane label="统计表" name="table">
              <el-table :data="tableData" stripe>
                <el-table-column prop="cluster_id" label="聚类ID" width="80" />
                <el-table-column prop="label" label="标签" width="120" />
                <el-table-column prop="size" label="规模" sortable />
                <el-table-column prop="avg_monetary" label="平均金额" sortable>
                  <template #default="{ row }">
                    ${{ row.avg_monetary.toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="avg_frequency" label="平均频次" sortable />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        
          <!-- 操作按钮 -->
          <div class="action-bar">
            <el-button type="primary" @click="generateReport">
              <el-icon><Document /></el-icon>
              生成AI报告
            </el-button>
            <el-button @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </div>
      
        <!-- 空状态 -->
        <el-empty v-else description="请配置参数并开始分析" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/store/analysis'
import { ElMessage } from 'element-plus'
import ScatterChart3D from '@/components/charts/ScatterChart3D.vue'
import RadarChart from '@/components/charts/RadarChart.vue'

const router = useRouter()
const analysisStore = useAnalysisStore()

const config = reactive({
  k: 3,
  features: ['rfm_frequency', 'rfm_monetary']
})

const progress = ref(0)
const activeTab = ref('scatter')

const handleStartAnalysis = async () => {
  try {
    // 模拟进度
    const interval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += 10
      }
    }, 500)
  
    await analysisStore.startClustering(config.k, config.features)
  
    clearInterval(interval)
    progress.value = 100
    ElMessage.success('分析完成！')
  } catch (error) {
    ElMessage.error('分析失败')
  }
}

const generateReport = () => {
  router.push({
    name: 'ReportGenerate',
    query: { cluster_id: analysisStore.clusterResults.cluster_id }
  })
}
</script>
```

##### 2.5.4 AI报告生成页

```vue
<!-- src/views/report/ReportGenerateView.vue -->
<template>
  <div class="report-generate">
    <el-row :gutter="16">
      <!-- 主对话区 -->
      <el-col :xs="24" :md="18">
        <el-card class="chat-card">
          <template #header>
            <div class="header">
              <el-avatar :size="32">🤖</el-avatar>
              <span class="title">AI 分析助手</span>
            </div>
          </template>
        
          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="message"
              :class="msg.role"
            >
              <el-avatar :size="40">
                {{ msg.role === 'user' ? '👤' : '🤖' }}
              </el-avatar>
            
              <div class="content">
                <!-- 用户消息 -->
                <div v-if="msg.role === 'user'" class="text">
                  {{ msg.content }}
                </div>
              
                <!-- AI消息（Markdown渲染） -->
                <div v-else class="markdown-body">
                  <MarkdownRenderer :content="msg.content" />
                
                  <!-- 内嵌图表 -->
                  <div v-if="msg.charts" class="charts">
                    <component
                      v-for="(chart, i) in msg.charts"
                      :key="i"
                      :is="chart.type"
                      :data="chart.data"
                    />
                  </div>
                </div>
              </div>
            </div>
          
            <!-- 加载中 -->
            <div v-if="isGenerating" class="message assistant">
              <el-avatar :size="40">🤖</el-avatar>
              <div class="content">
                <StreamingText :content="currentStream" />
              </div>
            </div>
          </div>
        
          <!-- 输入框 -->
          <div class="input-area">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="3"
              placeholder="输入您的问题或需求..."
              @keydown.enter.ctrl="handleSend"
            />
            <el-button
              type="primary"
              :loading="isGenerating"
              :disabled="!userInput.trim()"
              @click="handleSend"
            >
              发送 (Ctrl+Enter)
            </el-button>
          </div>
        </el-card>
      </el-col>
    
      <!-- 侧边栏 -->
      <el-col :xs="24" :md="6">
        <!-- 快速模板 -->
        <el-card title="快速模板">
          <el-button
            v-for="template in templates"
            :key="template.id"
            text
            @click="useTemplate(template.content)"
            class="template-btn"
          >
            {{ template.title }}
          </el-button>
        </el-card>
      
        <!-- 历史对话 -->
        <el-card title="历史报告" class="history-card">
          <el-timeline>
            <el-timeline-item
              v-for="report in recentReports"
              :key="report.id"
              :timestamp="report.created_at"
            >
              <el-link @click="loadReport(report.id)">
                {{ report.title }}
              </el-link>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { reportAPI } from '@/api/report'
import MarkdownRenderer from '@/components/report/MarkdownRenderer.vue'
import StreamingText from '@/components/report/StreamingText.vue'
import { SSEClient } from '@/utils/sse'

const route = useRoute()

const messages = ref<any[]>([])
const userInput = ref('')
const isGenerating = ref(false)
const currentStream = ref('')
const messageListRef = ref()

const templates = ref([
  { id: 1, title: '分析核心客户群', content: '请分析核心客户群的特征和营销策略' },
  { id: 2, title: '对比各聚类', content: '请对比各个聚类的差异' },
  { id: 3, title: '生成完整报告', content: '请生成一份完整的市场分析报告' }
])

const recentReports = ref([])

onMounted(async () => {
  // 加载历史报告
  const data = await reportAPI.getReports({ page: 1, page_size: 5 })
  recentReports.value = data.items
  
  // 如果有cluster_id参数，自动开始分析
  if (route.query.cluster_id) {
    userInput.value = '请分析这个聚类的特征'
    handleSend()
  }
})

const handleSend = async () => {
  if (!userInput.value.trim() || isGenerating.value) return
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value
  })
  
  const query = userInput.value
  userInput.value = ''
  
  // 开始生成
  isGenerating.value = true
  currentStream.value = ''
  
  try {
    // 调用生成API
    const { report_id, stream_url } = await reportAPI.generateReport({
      report_type: 'cluster_analysis',
      cluster_id: Number(route.query.cluster_id),
      custom_prompt: query
    })
  
    // 建立SSE连接
    const sseClient = new SSEClient()
    sseClient.connect(stream_url, (chunk) => {
      currentStream.value += chunk
      scrollToBottom()
    })
  
    sseClient.onComplete(() => {
      messages.value.push({
        role: 'assistant',
        content: currentStream.value
      })
      currentStream.value = ''
      isGenerating.value = false
    })
  } catch (error) {
    isGenerating.value = false
    ElMessage.error('生成失败')
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    messageListRef.value?.scrollTo({
      top: messageListRef.value.scrollHeight,
      behavior: 'smooth'
    })
  })
}

const useTemplate = (content: string) => {
  userInput.value = content
}
</script>

<style scoped lang="scss">
.report-generate {
  .chat-card {
    height: calc(100vh - 180px);
    display: flex;
    flex-direction: column;
  
    .header {
      display: flex;
      align-items: center;
      gap: 12px;
    
      .title {
        font-size: 18px;
        font-weight: 600;
      }
    }
  
    .message-list {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
    
      .message {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
      
        &.user {
          flex-direction: row-reverse;
        
          .content {
            background: $primary-color;
            color: white;
            border-radius: 16px 16px 0 16px;
          }
        }
      
        &.assistant {
          .content {
            background: $bg-color;
            border-radius: 16px 16px 16px 0;
          }
        }
      
        .content {
          flex: 1;
          padding: 16px;
          max-width: 80%;
        }
      }
    }
  
    .input-area {
      display: flex;
      gap: 12px;
      padding-top: 16px;
      border-top: 1px solid $border-color;
    }
  }
  
  .template-btn {
    display: block;
    width: 100%;
    text-align: left;
    margin-bottom: 8px;
  }
}
</style>
```

---

### 第三部分：关键工具与组件

#### 3.1 SSE客户端

```typescript
// src/utils/sse.ts
export class SSEClient {
  private eventSource: EventSource | null = null
  private onCompleteCallback: (() => void) | null = null
  
  connect(url: string, onMessage: (data: string) => void) {
    this.eventSource = new EventSource(url)
  
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close()
        this.onCompleteCallback?.()
        return
      }
      onMessage(event.data)
    }
  
    this.eventSource.onerror = (error) => {
      console.error('SSE Error:', error)
      this.close()
    }
  }
  
  onComplete(callback: () => void) {
    this.onCompleteCallback = callback
  }
  
  close() {
    this.eventSource?.close()
    this.eventSource = null
  }
}
```

#### 3.2 Markdown渲染组件

```vue
<!-- src/components/report/MarkdownRenderer.vue -->
<template>
  <div class="markdown-body" v-html="renderedHTML"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const props = defineProps<{
  content: string
}>()

const md = new MarkdownIt({
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {}
    }
    return ''
  }
})

const renderedHTML = computed(() => {
  return md.render(props.content)
})
</script>

<style>
@import 'highlight.js/styles/github.css';
@import 'github-markdown-css/github-markdown.css';
</style>
```

#### 3.3 ECharts 3D散点图组件

```vue
<!-- src/components/charts/ScatterChart3D.vue -->
<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'

const props = defineProps<{
  data: any[]
}>()

const chartRef = ref()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      formatter: (params: any) => `
        <div style="padding: 8px;">
          <strong>${params.name}</strong><br/>
          频次: ${params.value[0]}<br/>
          金额: ${params.value[1].toLocaleString()}<br/>
          聚类: ${params.value[3]}
        </div>
      `
    },
    grid3D: {
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 5,
        distance: 200
      },
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
    xAxis3D: {
      name: 'Frequency',
      type: 'value'
    },
    yAxis3D: {
      name: 'Monetary ($)',
      type: 'log',
      logBase: 10
    },
    zAxis3D: {
      name: 'Recency',
      type: 'value'
    },
    series: [{
      type: 'scatter3D',
      data: props.data,
      symbolSize: 5,
      itemStyle: {
        opacity: 0.7
      },
      emphasis: {
        itemStyle: {
          opacity: 1,
          borderWidth: 2,
          borderColor: '#fff'
        }
      }
    }]
  }
  
  chartInstance.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})

watch(() => props.data, () => {
  chartInstance?.setOption({
    series: [{ data: props.data }]
  })
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 500px;
}
</style>
```

---

## 📝 开发检查清单

### 后端开发清单

- [ ] **Phase 1: 基础架构**

  - [ ] FastAPI项目初始化
  - [ ] SQLAlchemy模型定义（7张表）
  - [ ] 数据库迁移脚本
  - [ ] JWT认证系统
  - [ ] 异常处理中间件
  - [ ] CORS配置
- [ ] **Phase 2: 核心API**

  - [ ] 用户认证API（注册、登录、获取信息）
  - [ ] 医生数据API（列表、详情、统计）
  - [ ] 分析任务API（创建、查询、状态）
  - [ ] AI报告API（生成、查询、流式输出）
  - [ ] 管理API（用户管理、日志）
- [ ] **Phase 3: 业务服务**

  - [ ] K-Means聚类服务
  - [ ] Dify集成服务
  - [ ] 数据导出服务
  - [ ] 任务队列管理
- [ ] **Phase 4: 测试与文档**

  - [ ] 单元测试（pytest）
  - [ ] API文档（Swagger自动生成）
  - [ ] 性能测试
  - [ ] Docker镜像构建

### 前端开发清单

- [ ] **Phase 1: 项目搭建**

  - [ ] Vite + Vue3 + TypeScript初始化
  - [ ] 路由配置
  - [ ] Pinia状态管理
  - [ ] Axios封装
  - [ ] Element Plus配置
- [ ] **Phase 2: 基础页面**

  - [ ] 登录/注册页
  - [ ] 主布局（侧边栏+顶栏）
  - [ ] Dashboard
  - [ ] 404页面
- [ ] **Phase 3: 核心功能**

  - [ ] 医生列表页（表格、筛选、分页）
  - [ ] 医生详情页
  - [ ] 聚类分析页（配置、可视化）
  - [ ] AI报告生成页（对话式）
  - [ ] 报告列表与详情
- [ ] **Phase 4: 高级组件**

  - [ ] ECharts图表组件（散点图、雷达图、折线图）
  - [ ] Markdown渲染组件
  - [ ] SSE流式组件
  - [ ] 数据导出组件
- [ ] **Phase 5: 优化与测试**

  - [ ] 响应式适配
  - [ ] 动画效果
  - [ ] 性能优化（懒加载、虚拟滚动）
  - [ ] E2E测试（Cypress）

### Dify配置清单

- [ ] **工作流设计**

  - [ ] 任务规划节点
  - [ ] 数据分析节点
  - [ ] 可视化生成节点
  - [ ] 报告撰写节点
- [ ] **工具开发**

  - [ ] 数据库查询工具
  - [ ] K-Means模型调用工具
  - [ ] 图表生成工具
- [ ] **知识库构建**

  - [ ] 医药行业知识库
  - [ ] 营销策略模板库
  - [ ] 常见问题库

---

## 🚀 开发最佳实践

### 1. 代码规范

- 使用Prettier格式化代码
- 使用ESLint检查代码质量
- 遵循Python PEP8规范
- TypeScript严格模式

### 2. Git工作流

```bash
# 功能分支开发
git checkout -b feature/user-auth
# 提交格式
git commit -m "feat: 实现用户认证功能"
git commit -m "fix: 修复登录页样式问题"
git commit -m "docs: 更新API文档"
```

### 3. 环境变量管理

```env
# backend/.env
DATABASE_URL=sqlite:///./pharma.db
SECRET_KEY=your-secret-key-change-in-production
DIFY_API_KEY=your-dify-api-key
DIFY_WORKFLOW_ID=your-workflow-id

# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1

# frontend/.env.production
VITE_API_BASE_URL=https://api.example.com/api/v1
```

### 4. Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./pharma.db
      - DIFY_API_KEY=${DIFY_API_KEY}
    volumes:
      - ./backend/pharma.db:/app/pharma.db
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

---

## ⚠️ 常见问题与解决方案

### 问题1：CORS跨域错误

**解决**：在FastAPI中配置CORS中间件

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 问题2：SQLite并发写入错误

**解决**：使用WAL模式或迁移到PostgreSQL

```python
# database.py
engine = create_engine(
    "sqlite:///./pharma.db",
    connect_args={"check_same_thread": False, "timeout": 30}
)
```

### 问题3：大数据量导致前端卡顿

**解决**：

- 后端实现分页
- 前端使用虚拟滚动（vue-virtual-scroller）
- 图表数据采样（显示1000个点而不是全部）

### 问题4：Dify API超时

**解决**：

- 增加httpx的timeout配置
- 实现异步任务队列（Celery）
- 添加重试机制

---

## 📚 学习资源

### 后端相关

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy教程](https://www.sqlalchemy.org/library.html)
- [K-Means算法详解](https://scikit-learn.org/stable/modules/clustering.html)

### 前端相关

- [Vue3官方文档](https://vuejs.org/)
- [Element Plus组件库](https://element-plus.org/)
- [ECharts示例](https://echarts.apache.org/examples/)

### Dify相关

- [Dify官方文档](https://docs.dify.ai/)
- [工作流最佳实践](https://docs.dify.ai/guides/workflow)

---

## 🎉 完成标准

当你完成以下所有功能时，即可交付项目：

✅ **用户可以注册登录**
✅ **可以查看和筛选医生数据**
✅ **可以执行K-Means聚类分析并看到可视化结果**
✅ **可以通过对话生成AI报告（流式输出）**
✅ **报告包含Markdown格式文本和内嵌图表**
✅ **系统运行稳定，无重大Bug**
✅ **代码注释清晰，有API文档**
✅ **通过Docker一键部署**
