# 🤖 医药市场智能分析系统 - AI Agent 开发总指令

> **项目代号**: PharmaAgentSystem
> **开发模式**: 模块化迭代开发
> **交付标准**: 可运行的Web应用 + 完整文档
> **开发周期**: 8周（分4个Phase）

---

## 📋 项目概述（给Agent的背景）

你正在开发一个基于LLM智能体的医药市场分析系统。该系统的目标用户是医药企业的市场分析师，他们需要：

1. **管理医生数据**：查询738,772名美国医生的RFM（Recency, Frequency, Monetary）特征
2. **执行聚类分析**：使用K-Means算法自动将医生分群
3. **生成AI报告**：通过Dify工作流，用自然语言对话生成专业的市场策略报告
4. **可视化展示**：通过ECharts图表直观展示分析结果

**核心技术栈**：

- 后端：Python 3.10+ + FastAPI + SQLAlchemy + SQLite
- 前端：Vue 3 + TypeScript + Element Plus + ECharts
- AI层：Dify平台 + Google Gemini LLM
- 算法：Scikit-learn (K-Means)

---

## 🎯 你需要完成的4个开发阶段

### Phase 1: 基础架构搭建（第1-2周）

**目标**：建立项目骨架，实现用户认证，完成数据库初始化

#### 1.1 后端任务

**创建项目结构**：

```
PharmaAgentSystem/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # 7张表的模型
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── payment.py
│   │   │   ├── analysis.py
│   │   │   ├── report.py
│   │   │   └── log.py
│   │   ├── schemas/             # Pydantic验证模型
│   │   ├── routers/             # API路由
│   │   │   ├── auth.py
│   │   │   ├── doctors.py
│   │   │   ├── analysis.py
│   │   │   ├── reports.py
│   │   │   └── admin.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── auth_service.py
│   │   │   ├── doctor_service.py
│   │   │   ├── analysis_service.py   # K-Means
│   │   │   └── dify_service.py       # Dify集成
│   │   └── core/
│   │       ├── security.py      # JWT + 密码加密
│   │       └── exceptions.py
│   ├── scripts/
│   │   └── init_db.py           # 初始化数据库脚本
│   └── pharma.db                # SQLite数据库（已存在）
└── frontend/                    # 暂不创建
```

**关键实现**：

1. **数据库模型** (`app/models/*.py`)：

```python
# models/user.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="viewer")  # admin/analyst/viewer
    created_at = Column(DateTime, server_default=func.now())

# models/doctor.py - 扩展现有表
class Doctor(Base):
    __tablename__ = "doctors"
    npi = Column(String(20), primary_key=True)
    full_name = Column(String(200))
    specialty = Column(String(200))
    state = Column(String(2))
    rfm_frequency = Column(Integer)
    rfm_monetary = Column(Float)
    rfm_recency = Column(Date)
    cluster_id = Column(Integer, ForeignKey("cluster_results.cluster_id"))
    cluster_label = Column(String(50))  # 新增：如"核心客户"

# 其他5张表参考设计文档...
```

2. **JWT认证** (`core/security.py`)：

```python
from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # 验证Token并返回User对象
    pass
```

3. **认证API** (`routers/auth.py`)：

```python
@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. 检查用户名是否存在
    # 2. 密码加密
    # 3. 创建用户
    # 4. 返回成功信息

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. 验证用户名密码
    # 2. 生成JWT Token
    # 3. 返回Token和用户信息

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
```

#### 1.2 前端任务

**创建项目**：

```bash
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install vue-router@4 pinia axios element-plus
npm install echarts vue-echarts sass -D
```

**关键文件**：

1. **Axios封装** (`src/utils/request.ts`)：

```typescript
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截：添加Token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一错误处理
request.interceptors.response.use(
  response => response.data.data,
  error => {
    if (error.response?.status === 401) {
      // 跳转到登录页
    }
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)
```

2. **用户Store** (`src/store/user.ts`)：

```typescript
export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as User | null
  }),
  
  actions: {
    async login(username: string, password: string) {
      const data = await authAPI.login({ username, password })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('token', data.access_token)
    },
  
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
```

3. **登录页** (`src/views/auth/LoginView.vue`)：

- 左右分栏布局
- 左侧：渐变蓝背景 + Logo + Slogan + 动态粒子背景
- 右侧：白色卡片 + 表单（用户名、密码、记住我）
- 提交后调用 `userStore.login()`

**Phase 1 交付标准**：
✅ 后端API运行在 http://localhost:8000
✅ Swagger文档可访问：http://localhost:8000/docs
✅ 用户可以注册、登录、获取个人信息
✅ 前端登录页完成，可以成功登录并跳转

---

### Phase 2: 核心功能开发（第3-4周）

**目标**：实现医生数据查询、K-Means聚类分析、结果可视化

#### 2.1 医生数据API

**后端实现** (`routers/doctors.py`)：

```python
@router.get("/doctors")
async def get_doctors(
    page: int = 1,
    page_size: int = 20,
    specialty: Optional[str] = None,
    state: Optional[str] = None,
    cluster_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 构建查询（支持多条件筛选）
    query = db.query(Doctor)
    if specialty: query = query.filter(Doctor.specialty == specialty)
    if state: query = query.filter(Doctor.state == state)
    if cluster_id is not None: query = query.filter(Doctor.cluster_id == cluster_id)
  
    # 2. 分页
    total = query.count()
    doctors = query.offset((page - 1) * page_size).limit(page_size).all()
  
    return {
        "total": total,
        "items": [DoctorSchema.from_orm(d) for d in doctors]
    }

@router.get("/doctors/{npi}")
async def get_doctor_detail(npi: str, db: Session = Depends(get_db)):
    # 返回医生详情 + 最近10条支付记录
    pass

@router.get("/doctors/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    # 返回总数、平均金额、专业分布、地区分布等
    pass
```

**前端实现** (`views/doctor/DoctorListView.vue`)：

- 顶部筛选栏（专业、州、聚类ID、金额范围）
- Element Plus Table组件展示数据
- 支持排序、分页
- 点击行跳转到详情页

#### 2.2 K-Means聚类服务

**后端实现** (`services/analysis_service.py`)：

```python
class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
  
    def perform_clustering(self, k: int, features: List[str] = None) -> ClusterResult:
        """执行K-Means聚类"""
        # 1. 加载数据
        doctors = self.db.query(Doctor).all()
        df = pd.DataFrame([{
            'npi': d.npi,
            'rfm_frequency': d.rfm_frequency,
            'rfm_monetary': d.rfm_monetary
        } for d in doctors])
    
        # 2. 特征标准化
        if not features:
            features = ['rfm_frequency', 'rfm_monetary']
        X = StandardScaler().fit_transform(df[features])
    
        # 3. 执行聚类
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X)
        df['cluster'] = labels
    
        # 4. 计算评估指标
        silhouette = silhouette_score(X, labels)
    
        # 5. 生成每个聚类的统计信息
        cluster_stats = {}
        for i in range(k):
            cluster_df = df[df['cluster'] == i]
            cluster_stats[str(i)] = {
                'size': len(cluster_df),
                'avg_monetary': float(cluster_df['rfm_monetary'].mean()),
                'avg_frequency': float(cluster_df['rfm_frequency'].mean()),
                'label': self._auto_label(cluster_df)  # 自动打标签
            }
    
        # 6. 保存到数据库
        result = ClusterResult(
            k_value=k,
            cluster_stats=json.dumps(cluster_stats),
            silhouette_score=silhouette,
            is_active=True
        )
    
        # 7. 更新doctors表的cluster_id
        for _, row in df.iterrows():
            self.db.query(Doctor).filter(Doctor.npi == row['npi']).update({
                'cluster_id': int(row['cluster']),
                'cluster_label': cluster_stats[str(row['cluster'])]['label']
            })
    
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result
```

**分析API** (`routers/analysis.py`)：

```python
@router.post("/clustering/perform")
async def perform_clustering(
    request: ClusteringRequest,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 创建任务记录
    task = AnalysisTask(
        task_name=request.task_name,
        task_type="clustering",
        parameters=json.dumps({"k": request.k}),
        created_by=current_user.id,
        status="pending"
    )
    db.add(task)
    db.commit()
  
    # 2. 后台执行聚类（避免阻塞）
    bg_tasks.add_task(run_clustering_task, task.task_id, request.k, db)
  
    return {
        "task_id": task.task_id,
        "status": "pending",
        "message": "Analysis started"
    }

@router.get("/clustering/results/{cluster_id}")
async def get_cluster_results(cluster_id: int, db: Session = Depends(get_db)):
    result = db.query(ClusterResult).filter(ClusterResult.cluster_id == cluster_id).first()
    if not result:
        raise HTTPException(404, "Result not found")
  
    return {
        "cluster_id": result.cluster_id,
        "k_value": result.k_value,
        "cluster_stats": json.loads(result.cluster_stats),
        "silhouette_score": result.silhouette_score,
        # 用于前端绘图的数据
        "visualization_data": self._prepare_viz_data(result)
    }
```

#### 2.3 聚类分析页

**前端实现** (`views/analysis/ClusterAnalysisView.vue`)：

**布局**：

- 左侧：配置面板（K值滑块、特征复选框、开始分析按钮）
- 右侧：结果展示区（进度条 → 评估指标卡片 → Tabs切换图表）

**图表组件**：

1. **3D散点图** (`components/charts/ScatterChart3D.vue`):

```vue
<template>
  <div ref="chartRef" style="height: 500px;"></div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts'
import 'echarts-gl'

const props = defineProps<{ data: any[] }>()
const chartRef = ref()

onMounted(() => {
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    grid3D: {
      viewControl: { autoRotate: true }
    },
    xAxis3D: { name: 'Frequency', type: 'value' },
    yAxis3D: { name: 'Monetary', type: 'log' },
    zAxis3D: { name: 'Recency', type: 'value' },
    series: [{
      type: 'scatter3D',
      data: props.data,
      symbolSize: 5
    }]
  })
})
</script>
```

2. **雷达图** - 对比各聚类的RFM特征
3. **统计表格** - 每个聚类的详细数据

**交互流程**：

1. 用户选择K=3，点击"开始分析"
2. 调用 `analysisStore.startClustering(3)`
3. 显示Loading进度条
4. 每2秒轮询任务状态
5. 完成后加载结果并渲染图表

**Phase 2 交付标准**：
✅ 可以查看和筛选医生列表
✅ 可以执行K-Means聚类（K=2-10）
✅ 聚类结果保存到数据库
✅ 前端显示3D散点图、雷达图和统计表
✅ Dashboard显示关键指标

---

### Phase 3: AI集成（第5-6周）

**目标**：集成Dify，实现自然语言驱动的AI报告生成

#### 3.1 Dify工作流配置

**在Dify平台创建工作流**（通过Web界面）：

```yaml
工作流结构：
1. 输入节点
   - 用户问题：user_query (Text)
   - 聚类数据：cluster_data (JSON)

2. LLM节点（任务规划）
   - 模型：gemini-1.5-pro
   - System Prompt：
     "你是医药市场分析专家。根据用户需求，制定分析计划。
      可用工具：数据库查询、聚类统计、图表生成。
      返回JSON格式的执行步骤。"

3. Code节点（数据处理）
   - 调用后端API获取详细数据
   - 计算统计指标
   - 生成图表配置

4. Knowledge Base节点
   - 查询医药营销知识库
   - 获取相关策略模板

5. LLM节点（报告撰写）
   - 模型：gemini-1.5-pro
   - System Prompt：
     "基于数据和知识库，撰写专业报告。
      包含：核心发现、数据分析、策略建议、风险提示。
      使用Markdown格式，嵌入图表配置。"

6. 输出节点
   - Markdown报告
   - 图表配置JSON
```

**知识库内容** (准备几个文本文件上传到Dify)：

- 医药行业术语词典
- 典型营销策略案例
- 合规要求清单
- 报告撰写模板

#### 3.2 后端Dify服务

**实现** (`services/dify_service.py`)：

```python
import httpx
from typing import AsyncGenerator

class DifyService:
    def __init__(self):
        self.base_url = os.getenv("DIFY_API_URL")
        self.api_key = os.getenv("DIFY_API_KEY")
        self.workflow_id = os.getenv("DIFY_WORKFLOW_ID")
  
    async def generate_report_stream(
        self,
        user_input: str,
        cluster_id: int
    ) -> AsyncGenerator[str, None]:
        """流式生成报告"""
        # 1. 获取聚类数据
        cluster_data = self._get_cluster_data(cluster_id)
    
        # 2. 调用Dify API
        async with httpx.AsyncClient(timeout=300) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/workflows/run",
                json={
                    "inputs": {
                        "user_query": user_input,
                        "cluster_data": cluster_data
                    },
                    "response_mode": "streaming"
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        yield chunk
```

**报告API** (`routers/reports.py`)：

```python
@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
  
    return {
        "report_id": report.report_id,
        "stream_url": f"/api/v1/reports/{report.report_id}/stream"
    }

@router.get("/{report_id}/stream")
async def stream_report(report_id: int, db: Session = Depends(get_db)):
    """SSE流式输出"""
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
  
    async def event_generator():
        dify_service = DifyService()
        full_content = ""
    
        async for chunk in dify_service.generate_report_stream(
            user_input=report.report_title,
            cluster_id=report.related_cluster_id
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

#### 3.3 前端报告生成页

**实现** (`views/report/ReportGenerateView.vue`)：

**布局**：

- 左侧：聊天界面（类ChatGPT）
- 右侧：快速模板 + 历史报告

**核心组件**：

1. **SSE客户端** (`utils/sse.ts`)：

```typescript
export class SSEClient {
  private eventSource: EventSource | null = null
  
  connect(url: string, onMessage: (chunk: string) => void) {
    this.eventSource = new EventSource(url)
  
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close()
        return
      }
      onMessage(event.data)
    }
  }
  
  close() {
    this.eventSource?.close()
  }
}
```

2. **Markdown渲染** (`components/report/MarkdownRenderer.vue`)：

```vue
<template>
  <div class="markdown-body" v-html="html"></div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const md = new MarkdownIt({
  highlight: (str, lang) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(str, { language: lang }).value
    }
    return ''
  }
})

const html = computed(() => md.render(props.content))
</script>
```

**交互流程**：

1. 用户输入："请分析核心客户群的特征"
2. 调用 `reportAPI.generateReport()` 获取 `report_id`
3. 建立SSE连接到 `/reports/{id}/stream`
4. 逐字渲染报告内容（打字机效果）
5. 完成后显示 [保存报告] [导出PDF] 按钮

**Phase 3 交付标准**：
✅ Dify工作流配置完成并测试通过
✅ 后端可以调用Dify API
✅ 前端可以流式接收报告内容
✅ 报告包含Markdown文本和图表
✅ 可以保存和查看历史报告

---

### Phase 4: 完善与优化（第7-8周）

**目标**：系统管理功能、性能优化、测试、部署

#### 4.1 系统管理模块

**后端**：

- 用户管理API（仅admin角色）
- 系统日志查询
- 健康检查接口

**前端**：

- 用户列表页（增删改查、角色管理）
- 系统日志页（表格展示、导出）
- 个人设置页（修改密码、头像）

#### 4.2 性能优化

1. **后端优化**：

   - 为常用查询添加数据库索引
   - 实现Redis缓存（可选）
   - 使用连接池管理数据库连接
2. **前端优化**：

   - 路由懒加载
   - 大列表使用虚拟滚动
   - 图表数据采样（显示抽样数据）
   - 图片使用CDN

#### 4.3 Docker部署

**创建Dockerfile**：

```dockerfile
# backend/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml**：

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
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

#### 4.4 测试

**后端测试** (pytest)：

```python
# tests/test_auth.py
def test_login_success(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "test",
        "password": "test123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

# tests/test_analysis.py
def test_clustering(client, auth_header):
    response = client.post(
        "/api/v1/analysis/clustering/perform",
        json={"k": 3, "task_name": "Test"},
        headers=auth_header
    )
    assert response.status_code == 202
```

**前端测试** (Vitest)：

```typescript
// tests/unit/LoginView.spec.ts
describe('LoginView', () => {
  it('should login successfully', async () => {
    const wrapper = mount(LoginView)
    await wrapper.find('input[name="username"]').setValue('test')
    await wrapper.find('input[name="password"]').setValue('test123')
    await wrapper.find('button[type="submit"]').trigger('click')
    expect(wrapper.emitted('login')).toBeTruthy()
  })
})
```

**Phase 4 交付标准**：
✅ 系统管理功能完善
✅ 性能优化完成，页面加载<3秒
✅ 单元测试覆盖率>60%
✅ Docker镜像构建成功
✅ 部署文档编写完成

---

## 🎨 UI/UX设计要求

### 设计关键词

Clean（干净）、Professional（专业）、Data-Driven（数据驱动）、Trustworthy（值得信赖）

### 配色方案

```scss
$primary-color: #1890FF;       // 科技蓝（主按钮）
$success-color: #52C41A;       // 成功/增长
$warning-color: #FAAD14;       // 警告
$danger-color: #F5222D;        // 错误/下降
$bg-color: #F0F2F5;            // 背景
$text-primary: #262626;        // 标题
$text-secondary: #595959;      // 正文
```

### 动画效果要求

1. **页面切换**：fade-slide过渡，持续0.3秒
2. **数字滚动**：使用CountUp.js，持续2秒
3. **卡片悬停**：translateY(-4px) + shadow增强
4. **图表加载**：渐入动画，持续0.5秒
5. **按钮点击**：波纹效果（Element Plus自带）

### 响应式断点

- Mobile: <768px（侧边栏折叠）
- Tablet: 768-1024px（卡片2列）
- Desktop: >1024px（卡片4列）

---

## ⚠️ 开发注意事项

### 关键约束

1. **不要使用localStorage存储敏感数据**，仅存储Token
2. **所有API必须有权限校验**（除了login/register）
3. **K-Means聚类要在后台任务执行**，避免阻塞请求
4. **Dify API调用超时设置为300秒**
5. **前端必须处理SSE连接断开**的情况

### 常见错误预防

1. **CORS问题**：FastAPI配置CORS中间件，允许前端域名
2. **SQLite并发问题**：设置timeout=30，或使用WAL模式
3. **大数据量卡顿**：后端强制分页，前端虚拟滚动
4. **Token过期**：前端拦截401，自动跳转登录页

### 代码风格

- Python：遵循PEP8，使用Black格式化
- TypeScript：使用Prettier，2空格缩进
- 提交信息：`feat: 新功能`, `fix: 修复`, `docs: 文档`

---

## 📦 最终交付清单

当你完成以下所有内容，即可提交项目：

### 代码

- [ ] 后端代码（FastAPI项目，完整注释）
- [ ] 前端代码（Vue3项目，完整注释）
- [ ] 数据库初始化脚本
- [ ] Docker配置文件
- [ ] requirements.txt / package.json

### 文档

- [ ] README.md（项目介绍、安装步骤、使用说明）
- [ ] API文档（Swagger自动生成）
- [ ] 部署文档（DEPLOYMENT.md）
- [ ] Dify配置指南（DIFY_SETUP.md）

### 测试

- [ ] 后端单元测试（>60%覆盖率）
- [ ] 前端组件测试
- [ ] 端到端测试用例

## 🚀 开始开发

**第一步**：创建项目目录并初始化

```bash
mkdir PharmaAgentSystem
cd PharmaAgentSystem
mkdir backend frontend docs
```

**第二步**：按Phase 1开始开发后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic bcrypt python-jose
# 创建app/main.py...
```

**第三步**：验证后端运行

```bash
uvicorn app.main:app --reload
# 访问 http://localhost:8000/docs
```

**第四步**：开发前端

```bash
cd ../frontend
npm create vite@latest . -- --template vue-ts
npm install
# 配置vite.config.ts...
npm run dev
```

**祝你开发顺利！有任何问题随时查阅设计文档。** 🎉
