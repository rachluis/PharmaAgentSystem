# 医药市场智能分析系统 - 完整设计文档

## 📋 目录

1. [系统架构设计](#1-系统架构设计)
2. [数据库设计](#2-数据库设计)
3. [后端API设计](#3-后端api设计)
4. [前端页面设计](#4-前端页面设计)
5. [Dify集成方案](#5-dify集成方案)
6. [完整项目目录](#6-完整项目目录)
7. [UI/UX设计规范](#7-uiux设计规范)

---

## 1. 系统架构设计

### 1.1 技术架构图

```
┌─────────────────────────────────────────────────────────┐
│                      前端层 (Vue3)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ 登录注册  │ 数据看板  │ 医生画像  │ AI报告   │ 系统管理│ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕ (HTTP/REST API)
┌─────────────────────────────────────────────────────────┐
│                   后端层 (FastAPI)                        │
│  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │
│  │ 用户认证  │ 数据查询  │ 分析服务  │ AI集成   │ 任务队列│ │
│  └──────────┴──────────┴──────────┴──────────┴────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   数据层 & AI层                          │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │ SQLite   │ K-Means  │ Dify     │ Gemini LLM      │  │
│  │ Database │ Model    │ Workflow │ API             │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心模块划分

#### 1.2.1 用户认证模块

- JWT Token认证
- 角色权限管理（Admin/Analyst/Viewer）
- 登录日志记录

#### 1.2.2 数据管理模块

- 医生数据CRUD
- 支付记录查询
- 数据导入导出

#### 1.2.3 分析引擎模块

- K-Means聚类执行
- RFM特征计算
- 聚类结果可视化

#### 1.2.4 AI报告生成模块

- Dify工作流调用
- 报告历史管理
- 流式输出支持

#### 1.2.5 系统管理模块

- 用户管理
- 系统日志
- 配置管理

---

## 2. 数据库设计

### 2.1 ER图关系

```
users (用户表)
  │
  ├──< analysis_tasks (分析任务表)
  │     │
  │     └──< cluster_results (聚类结果表)
  │
  └──< ai_reports (AI报告表)

doctors (医生表)
  │
  └──< payment_records (支付记录表)
```

### 2.2 数据表详细设计

#### 表1: users (用户表)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt加密
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'viewer',  -- admin/analyst/viewer
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### 表2: doctors (医生表 - 已存在，扩展)

```sql
CREATE TABLE doctors (
    npi VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(200),  -- 新增：冗余字段加速查询
    specialty VARCHAR(200),
    state VARCHAR(2),
    city VARCHAR(100),  -- 新增
  
    -- RFM特征
    rfm_recency DATE,
    rfm_frequency INTEGER,
    rfm_monetary REAL,
  
    -- 聚类结果
    cluster_id INTEGER,
    cluster_label VARCHAR(50),  -- 新增：如"核心客户"
  
    -- 统计字段
    total_payments INTEGER DEFAULT 0,
    avg_payment_amount REAL DEFAULT 0,
    last_payment_date DATE,
  
    -- 元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (cluster_id) REFERENCES cluster_results(cluster_id)
);

-- 索引
CREATE INDEX idx_doctors_specialty ON doctors(specialty);
CREATE INDEX idx_doctors_state ON doctors(state);
CREATE INDEX idx_doctors_cluster ON doctors(cluster_id);
CREATE INDEX idx_doctors_monetary ON doctors(rfm_monetary DESC);
```

#### 表3: payment_records (支付记录表)

```sql
CREATE TABLE payment_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    npi VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    amount REAL NOT NULL,
    payment_type VARCHAR(100),  -- 如"Consulting Fee"
    nature_of_payment VARCHAR(200),
    payer_name VARCHAR(200),
  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (npi) REFERENCES doctors(npi)
);

-- 索引
CREATE INDEX idx_payments_npi ON payment_records(npi);
CREATE INDEX idx_payments_date ON payment_records(payment_date);
CREATE INDEX idx_payments_amount ON payment_records(amount DESC);
```

#### 表4: analysis_tasks (分析任务表)

```sql
CREATE TABLE analysis_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name VARCHAR(200) NOT NULL,
    task_type VARCHAR(50) NOT NULL,  -- 'clustering', 'rfm_analysis'
  
    -- 任务参数（JSON格式）
    parameters TEXT,  -- 如 {"k": 3, "algorithm": "k-means"}
  
    -- 任务状态
    status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed
    progress INTEGER DEFAULT 0,  -- 0-100
  
    -- 执行信息
    created_by INTEGER,
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,
  
    -- 结果引用
    result_id INTEGER,
  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (result_id) REFERENCES cluster_results(cluster_id)
);

-- 索引
CREATE INDEX idx_tasks_status ON analysis_tasks(status);
CREATE INDEX idx_tasks_created_by ON analysis_tasks(created_by);
```

#### 表5: cluster_results (聚类结果表 - 扩展)

```sql
CREATE TABLE cluster_results (
    cluster_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,  -- 新增：关联分析任务
  
    -- 聚类配置
    k_value INTEGER NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'k-means',
  
    -- 聚类特征（JSON格式）
    features_used TEXT,  -- ["rfm_frequency", "rfm_monetary"]
  
    -- 聚类统计（JSON格式）
    cluster_stats TEXT,  -- {"0": {"size": 316000, "avg_monetary": 7713}, ...}
  
    -- 业务标签
    cluster_labels TEXT,  -- {"0": "核心客户", "1": "大众客户"}
  
    -- 模型评估
    silhouette_score REAL,
    inertia REAL,
  
    -- AI生成策略
    ai_strategy TEXT,
    strategy_generated_at DATETIME,
  
    -- 可视化数据（JSON格式）
    visualization_data TEXT,  -- 用于前端ECharts渲染
  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,  -- 当前激活的聚类方案
  
    FOREIGN KEY (task_id) REFERENCES analysis_tasks(task_id)
);
```

#### 表6: ai_reports (AI报告表)

```sql
CREATE TABLE ai_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_title VARCHAR(300) NOT NULL,
    report_type VARCHAR(50) NOT NULL,  -- 'cluster_analysis', 'doctor_profile', 'market_strategy'
  
    -- 报告内容
    report_content TEXT NOT NULL,  -- Markdown格式
    report_summary TEXT,  -- 摘要
  
    -- 关联数据
    related_cluster_id INTEGER,
    related_npi VARCHAR(20),
  
    -- 生成信息
    generated_by INTEGER,  -- 用户ID
    dify_conversation_id VARCHAR(100),  -- Dify对话ID
    dify_workflow_id VARCHAR(100),
    generation_time REAL,  -- 生成耗时（秒）
  
    -- 状态
    status VARCHAR(20) DEFAULT 'draft',  -- draft/published/archived
    view_count INTEGER DEFAULT 0,
  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (generated_by) REFERENCES users(id),
    FOREIGN KEY (related_cluster_id) REFERENCES cluster_results(cluster_id)
);

-- 索引
CREATE INDEX idx_reports_type ON ai_reports(report_type);
CREATE INDEX idx_reports_user ON ai_reports(generated_by);
CREATE INDEX idx_reports_created ON ai_reports(created_at DESC);
```

#### 表7: system_logs (系统日志表)

```sql
CREATE TABLE system_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,  -- 'login', 'analysis', 'export'
    module VARCHAR(50),  -- 'auth', 'analysis', 'report'
    ip_address VARCHAR(50),
    user_agent TEXT,
    request_data TEXT,  -- JSON格式
    response_status INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 索引
CREATE INDEX idx_logs_user ON system_logs(user_id);
CREATE INDEX idx_logs_action ON system_logs(action);
CREATE INDEX idx_logs_created ON system_logs(created_at DESC);
```

---

## 3. 后端API设计

### 3.1 API基础规范

#### 3.1.1 URL结构

```
/api/v1/{module}/{resource}/{action}
```

#### 3.1.2 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-12-14T10:00:00Z"
}
```

#### 3.1.3 错误响应

```json
{
  "code": 400,
  "message": "Invalid parameters",
  "detail": "k must be between 2 and 10",
  "timestamp": "2025-12-14T10:00:00Z"
}
```

### 3.2 API端点清单

#### 3.2.1 认证模块 (`/api/v1/auth`)

##### POST /auth/register

注册新用户

```json
// Request
{
  "username": "analyst01",
  "email": "analyst@example.com",
  "password": "SecurePass123!",
  "full_name": "张三"
}

// Response
{
  "code": 201,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "username": "analyst01",
    "role": "viewer"
  }
}
```

##### POST /auth/login

用户登录

```json
// Request
{
  "username": "analyst01",
  "password": "SecurePass123!"
}

// Response
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "analyst01",
      "role": "analyst",
      "avatar_url": "/avatars/default.png"
    }
  }
}
```

##### POST /auth/logout

用户登出

##### GET /auth/me

获取当前用户信息

##### PUT /auth/profile

更新个人信息

##### POST /auth/change-password

修改密码

---

#### 3.2.2 医生数据模块 (`/api/v1/doctors`)

##### GET /doctors

分页查询医生列表

```json
// Query Parameters
?page=1&page_size=20&specialty=Cardiology&state=CA&cluster_id=0

// Response
{
  "code": 200,
  "data": {
    "total": 738772,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "npi": "1234567890",
        "full_name": "Dr. John Smith",
        "specialty": "Cardiology",
        "state": "CA",
        "rfm_monetary": 15000.00,
        "rfm_frequency": 25,
        "cluster_label": "核心客户"
      }
    ]
  }
}
```

##### GET /doctors/

获取单个医生详情

```json
// Response
{
  "code": 200,
  "data": {
    "npi": "1234567890",
    "full_name": "Dr. John Smith",
    "specialty": "Cardiology",
    "state": "CA",
    "city": "Los Angeles",
    "rfm": {
      "recency": "2024-12-01",
      "frequency": 25,
      "monetary": 15000.00
    },
    "cluster": {
      "id": 0,
      "label": "核心客户",
      "characteristics": "高价值高活跃度客户"
    },
    "payment_history": [
      {
        "date": "2024-12-01",
        "amount": 1500.00,
        "type": "Consulting Fee"
      }
    ]
  }
}
```

##### GET /doctors/statistics

获取医生数据统计

```json
// Response
{
  "code": 200,
  "data": {
    "total_doctors": 738772,
    "total_payments": 2495000000.00,
    "avg_payment": 3377.92,
    "specialty_distribution": {
      "Cardiology": 50000,
      "Oncology": 45000
    },
    "state_distribution": {
      "CA": 120000,
      "NY": 95000
    }
  }
}
```

---

#### 3.2.3 分析模块 (`/api/v1/analysis`)

##### POST /analysis/clustering/perform

触发聚类分析

```json
// Request
{
  "k": 3,
  "features": ["rfm_frequency", "rfm_monetary"],
  "task_name": "2024年度医生分群",
  "description": "基于RFM特征的客户细分"
}

// Response
{
  "code": 202,
  "message": "Analysis task created",
  "data": {
    "task_id": 101,
    "status": "pending",
    "estimated_time": 120  // 秒
  }
}
```

##### GET /analysis/clustering/results/

获取聚类结果详情

```json
// Response
{
  "code": 200,
  "data": {
    "cluster_id": 1,
    "k_value": 3,
    "cluster_stats": {
      "0": {
        "size": 200000,
        "label": "顶级客户",
        "avg_monetary": 12000,
        "avg_frequency": 30,
        "characteristics": ["高价值", "高活跃"]
      },
      "1": {
        "size": 300000,
        "label": "潜力客户",
        "avg_monetary": 3500,
        "avg_frequency": 15
      },
      "2": {
        "size": 238772,
        "label": "大众客户",
        "avg_monetary": 200,
        "avg_frequency": 5
      }
    },
    "silhouette_score": 0.68,
    "visualization_data": {
      "scatter_3d": [...],
      "radar_chart": [...]
    }
  }
}
```

##### GET /analysis/tasks

获取分析任务列表

##### GET /analysis/tasks//status

查询任务状态

```json
// Response
{
  "code": 200,
  "data": {
    "task_id": 101,
    "status": "running",
    "progress": 45,
    "message": "Performing K-Means clustering..."
  }
}
```

---

#### 3.2.4 AI报告模块 (`/api/v1/reports`)

##### POST /reports/generate

生成AI报告（调用Dify）

```json
// Request
{
  "report_type": "cluster_analysis",
  "cluster_id": 1,
  "custom_prompt": "请重点分析核心客户群的特征和营销策略",
  "include_visualizations": true
}

// Response (流式)
{
  "code": 200,
  "data": {
    "report_id": 501,
    "status": "generating",
    "stream_url": "/api/v1/reports/501/stream"
  }
}
```

##### GET /reports//stream

SSE流式输出报告内容

```
// Server-Sent Events
data: {"type": "title", "content": "# 核心客户群分析报告"}
data: {"type": "section", "content": "## 一、群体特征分析"}
data: {"type": "text", "content": "该客户群共包含..."}
data: {"type": "chart", "content": {...}}
data: {"type": "done"}
```

##### GET /reports

获取报告列表

```json
// Query Parameters
?page=1&page_size=10&report_type=cluster_analysis&status=published

// Response
{
  "code": 200,
  "data": {
    "total": 50,
    "items": [
      {
        "report_id": 501,
        "title": "2024年度核心客户分析报告",
        "type": "cluster_analysis",
        "summary": "本报告针对...",
        "created_at": "2024-12-14T10:00:00Z",
        "view_count": 25
      }
    ]
  }
}
```

##### GET /reports/

获取报告详情

##### PUT /reports//publish

发布报告

##### DELETE /reports/

删除报告

---

#### 3.2.5 系统管理模块 (`/api/v1/admin`)

##### GET /admin/users

用户管理（需要admin权限）

##### PUT /admin/users//role

修改用户角色

##### GET /admin/logs

查看系统日志

##### GET /admin/system/health

系统健康检查

```json
// Response
{
  "code": 200,
  "data": {
    "status": "healthy",
    "database": "ok",
    "dify_connection": "ok",
    "uptime": 86400,
    "memory_usage": "45%"
  }
}
```

---

## 4. 前端页面设计

### 4.1 页面路由规划

```javascript
const routes = [
  // 公开路由
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  
  // 需要认证的路由
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'doctors', component: DoctorListView },
      { path: 'doctors/:npi', component: DoctorDetailView },
      { path: 'analysis', component: ClusterAnalysisView },
      { path: 'analysis/results/:id', component: AnalysisResultView },
      { path: 'reports', component: ReportListView },
      { path: 'reports/:id', component: ReportDetailView },
      { path: 'reports/generate', component: ReportGenerateView },
  
      // 管理员路由
      { 
        path: 'admin', 
        component: AdminLayout,
        meta: { requiresAdmin: true },
        children: [
          { path: 'users', component: UserManageView },
          { path: 'logs', component: SystemLogsView }
        ]
      }
    ]
  }
]
```

### 4.2 核心页面详细设计

#### 4.2.1 登录页 (LoginView)

**布局**：左右分栏

```
┌──────────────────────────────────────────────────┐
│ [左侧：渐变蓝背景 + 品牌插画]  │ [右侧：登录表单]    │
│                                │                  │
│  🏥 Logo                       │  ┌─────────────┐ │
│  医药市场智能分析系统            │  │  用户登录     │ │
│                                │  └─────────────┘ │
│  "数据驱动决策，智能赋能医疗"    │                  │
│                                │  用户名: [______] │
│  [动态数据可视化背景动画]        │  密码:   [______] │
│                                │                  │
│                                │  [ 记住我 ]      │
│                                │  [登录] [注册]   │
└──────────────────────────────────────────────────┘
```

**交互设计**：

- 输入框获得焦点时，左侧插画有微动画响应
- 登录按钮采用渐变蓝色，hover时有光晕效果
- 登录成功后，页面渐隐切换到Dashboard

#### 4.2.2 Dashboard (数据看板)

**核心指标卡片**（顶部4个）：

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 📊 总医生数  │ 💰 总金额    │ 📈 平均金额  │ ⏱ 最近分析  │
│  738,772   │ $2.50B     │  $3,377    │  2小时前    │
│  ↑ 2.3%    │ ↑ 5.1%     │ ↑ 1.8%     │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**图表区域**（中间两栏）：

- **左侧**：专业分布饼图 + 地区分布地图
- **右侧**：月度趋势折线图 + 聚类分布条形图

**快速操作区**（底部）：

- [开始新分析] [查看报告] [导出数据]

**动态效果**：

- 数字滚动动画（CountUp）
- 图表渐入动画
- 实时数据更新提示（右上角小红点）

#### 4.2.3 医生列表页 (DoctorListView)

**顶部筛选栏**：

```
┌────────────────────────────────────────────────────┐
│ 专业: [下拉选择▼] 州: [下拉▼] 聚类: [下拉▼]        │
│ 金额范围: [滑块: $0 ────●──── $50K]               │
│ [搜索: NPI/姓名_______] [重置] [搜索]              │
└────────────────────────────────────────────────────┘
```

**表格**（Element Plus Table）：

| NPI | 姓名 | 专业 | 州  | RFM频次 | RFM金额 | 聚类标签   | 操作         |
| --- | ---- | ---- | --- | ------- | ------- | ---------- | ------------ |
| ... | ...  | ...  | ... | ...     | ...     | 🏆核心客户 | [详情][分析] |

**交互增强**：

- 表头排序（点击表头可排序）
- 行悬停高亮
- 聚类标签使用不同颜色徽章（Tag）
- 分页器带跳转功能

#### 4.2.4 聚类分析页 (ClusterAnalysisView)

**配置面板**（左侧卡片）：

```
┌─────────────────────────┐
│ 聚类配置                 │
├─────────────────────────┤
│ K值: [滑块 2─●─10]       │
│ 特征选择:                │
│ ☑ RFM频次               │
│ ☑ RFM金额               │
│ ☐ 最近交互时间           │
│                         │
│ [开始分析] [查看历史]    │
└─────────────────────────┘
```

**结果展示**（右侧大区域）：

- **顶部**：分析进度条（分析中时显示）
- **图表区**：
  - **3D散点图**（可旋转交互）
  - **雷达图**（各聚类特征对比）
  - **箱线图**（金额分布）
- **表格**：各聚类统计数据

**动态效果**：

- 分析时显示Loading骨架屏
- 图表数据逐步加载动画
- 3D散点图支持鼠标拖拽旋转

#### 4.2.5 AI报告生成页 (ReportGenerateView)

**对话式界面**（类ChatGPT）：

```
┌─────────────────────────────────────────────┐
│ 🤖 AI 分析助手                               │
├─────────────────────────────────────────────┤
│                                             │
│  [用户] 请分析核心客户群的特征               │
│                                             │
│  [AI] 正在为您分析...                       │
│  ┌─────────────────────┐                   │
│  │ 核心客户群分析报告   │ [生成中 ⏳]        │
│  │ 1. 群体特征          │                   │
│  │ 2. 营销策略建议      │                   │
│  │ ...                 │                   │
│  └─────────────────────┘                   │
│                                             │
├─────────────────────────────────────────────┤
│ 💬 [输入您的问题...___________] [发送]       │
└─────────────────────────────────────────────┘
```

**侧边栏**（右侧）：

- **快速模板**：预设分析模板按钮
- **历史对话**：最近的报告列表

**交互亮点**：

- 打字机效果（流式输出）
- Markdown渲染（代码高亮、表格）
- 图表内嵌显示
- [保存报告] [导出PDF] 按钮

---

## 5. Dify集成方案

### 5.1 Dify架构设计

#### 5.1.1 工作流设计

```
用户输入（自然语言）
     ↓
[任务规划Agent] 
     ├→ 理解意图
     └→ 拆解子任务
     ↓
[数据分析Agent]
     ├→ 调用工具：数据库查询
     ├→ 调用工具：K-Means模型
     └→ 输出结构化数据
     ↓
[可视化Agent]
     ├→ 接收数据
     ├→ 选择图表类型
     └→ 生成ECharts配置
     ↓
[报告撰写Agent]
     ├→ 知识库查询（医药领域知识）
     ├→ 整合数据+图表
     └→ 生成Markdown报告
     ↓
返回给用户
```

### 5.2 Dify工具开发

#### 5.2.1 工具1：数据库查询工具

```python
# backend/app/dify_tools/database_query.py
from typing import Dict, List

def query_doctor_by_cluster(cluster_id: int, limit: int = 100) -> List[Dict]:
    """查询指定聚类的医生列表"""
    pass

def query_cluster_statistics(cluster_id: int) -> Dict:
    """获取聚类统计信息"""
    pass

def query_payment_trends(npi: str, months: int = 12) -> List[Dict]:
    """查询医生支付趋势"""
    pass
```

#### 5.2.2 工具2：K-Means模型调用

```python
# backend/app/dify_tools/clustering_tool.py
def get_cluster_info(cluster_id: int) -> Dict:
    """获取聚类详细信息"""
    return {
        "cluster_id": cluster_id,
        "label": "核心客户",
        "size": 316000,
        "avg_monetary": 7713.5,
        "characteristics": ["高价值", "高活跃"]
    }

def predict_doctor_cluster(npi: str) -> Dict:
    """预测医生所属聚类"""
    pass
```

#### 5.2.3 工具3：可视化配置生成

```python
# backend/app/dify_tools/chart_generator.py
def generate_radar_chart_config(cluster_stats: Dict) -> Dict:
    """生成雷达图ECharts配置"""
    return {
        "type": "radar",
        "data": [...],
        "option": {...}
    }

def generate_scatter_3d_config(doctor_data: List[Dict]) -> Dict:
    """生成3D散点图配置"""
    pass
```

### 5.3 Dify工作流配置

#### 5.3.1 节点配置示例

**节点1：任务规划节点**

```yaml
type: LLM
model: gemini-1.5-pro
system_prompt: |
  你是一个医药市场分析专家。根据用户的需求，制定详细的分析计划。
  可用工具：数据库查询、聚类模型、图表生成
  
  用户输入: {user_input}
  
  请返回JSON格式的任务计划:
  {
    "intent": "cluster_analysis",
    "steps": [
      {"action": "query_cluster_stats", "params": {"cluster_id": 0}},
      {"action": "generate_radar_chart", "params": {...}}
    ]
  }
```

**节点2：数据分析节点**

```yaml
type: Code
language: python
code: |
  import json
  from dify_tools.database_query import query_cluster_statistics
  
  cluster_id = context['cluster_id']
  stats = query_cluster_statistics(cluster_id)
  
  return {
    "stats": stats,
    "next_action": "generate_chart"
  }
```

**节点3：报告生成节点**

```yaml
type: LLM
model: gemini-1.5-pro
system_prompt: |
  基于以下数据，撰写一份专业的医药市场分析报告:
  
  聚类统计: {cluster_stats}
  图表配置: {chart_config}
  
  知识库: [医药营销策略知识库]
  
  请按以下结构输出Markdown格式报告:
  # 报告标题
  ## 一、核心发现
  ## 二、数据分析
  ## 三、策略建议
  ## 四、风险提示
```

### 5.4 后端集成代码

#### 5.4.1 Dify API客户端

```python
# backend/app/services/dify_service.py
import httpx
from typing import AsyncGenerator

class DifyService:
    def __init__(self):
        self.base_url = "https://api.dify.ai/v1"
        self.api_key = os.getenv("DIFY_API_KEY")
  
    async def generate_report_stream(
        self, 
        user_input: str,
        cluster_data: dict
    ) -> AsyncGenerator[str, None]:
        """流式生成报告"""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/workflows/run",
                json={
                    "inputs": {
                        "user_input": user_input,
                        "cluster_data": cluster_data
                    }
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                async for chunk in response.aiter_text():
                    yield chunk
  
    async def call_tool(self, tool_name: str, params: dict) -> dict:
        """调用Dify工具"""
        pass
```

#### 5.4.2 FastAPI流式端点

```python
# backend/app/routers/reports.py
from fastapi.responses import StreamingResponse

@router.get("/reports/{report_id}/stream")
async def stream_report(report_id: int):
    """SSE流式输出报告"""
    dify_service = DifyService()
  
    async def event_generator():
        async for chunk in dify_service.generate_report_stream(...):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
  
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 5.5 前端Dify流式接收

```typescript
// frontend/src/utils/sse.ts
export class SSEClient {
  private eventSource: EventSource | null = null;
  
  connect(url: string, onMessage: (data: string) => void) {
    this.eventSource = new EventSource(url);
  
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close();
        return;
      }
      onMessage(event.data);
    };
  }
  
  close() {
    this.eventSource?.close();
  }
}

// 使用示例
const sseClient = new SSEClient();
sseClient.connect('/api/v1/reports/501/stream', (chunk) => {
  reportContent.value += chunk;  // 追加内容
});
```

---

## 6. 完整项目目录

```
PharmaAgentSystem/
├── README.md                    # 项目说明
├── .gitignore
├── docker-compose.yml           # Docker编排
├── .env.example                 # 环境变量模板
│
├── backend/                     # 后端项目
│   ├── README.md
│   ├── requirements.txt         # Python依赖
│   ├── Dockerfile
│   ├── .env
│   ├── alembic.ini              # 数据库迁移配置
│   │
│   ├── app/                     # 主应用
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── dependencies.py      # 依赖注入
│   │   │
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── analysis.py
│   │   │   └── report.py
│   │   │
│   │   ├── schemas/             # Pydantic模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── doctor.py
│   │   │   ├── analysis.py
│   │   │   └── report.py
│   │   │
│   │   ├── routers/             # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # 认证接口
│   │   │   ├── doctors.py       # 医生数据接口
│   │   │   ├── analysis.py      # 分析接口
│   │   │   ├── reports.py       # 报告接口
│   │   │   └── admin.py         # 管理接口
│   │   │
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── doctor_service.py
│   │   │   ├── analysis_service.py  # K-Means聚类
│   │   │   ├── dify_service.py      # Dify集成
│   │   │   └── report_service.py
│   │   │
│   │   ├── core/                # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── security.py      # JWT/密码哈希
│   │   │   ├── exceptions.py    # 自定义异常
│   │   │   └── logger.py        # 日志配置
│   │   │
│   │   ├── dify_tools/          # Dify工具集
│   │   │   ├── __init__.py
│   │   │   ├── database_query.py
│   │   │   ├── clustering_tool.py
│   │   │   └── chart_generator.py
│   │   │
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       ├── data_processor.py
│   │       └── validators.py
│   │
│   ├── scripts/                 # 脚本
│   │   ├── etl_process.py       # 数据导入
│   │   ├── init_db.py           # 初始化数据库
│   │   └── create_admin.py      # 创建管理员
│   │
│   ├── notebooks/               # Jupyter实验
│   │   ├── clustering_experiment.ipynb
│   │   └── data_exploration.ipynb
│   │
│   ├── tests/                   # 测试
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_services.py
│   │
│   └── pharma.db                # SQLite数据库
│
├── frontend/                    # 前端项目
│   ├── README.md
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── .env.development
│   ├── .env.production
│   │
│   ├── public/                  # 静态资源
│   │   ├── favicon.ico
│   │   └── logo.png
│   │
│   ├── src/
│   │   ├── main.ts              # 入口文件
│   │   ├── App.vue
│   │   │
│   │   ├── router/              # 路由
│   │   │   ├── index.ts
│   │   │   └── guards.ts        # 路由守卫
│   │   │
│   │   ├── store/               # Pinia状态管理
│   │   │   ├── index.ts
│   │   │   ├── user.ts
│   │   │   ├── analysis.ts
│   │   │   └── report.ts
│   │   │
│   │   ├── api/                 # API封装
│   │   │   ├── index.ts
│   │   │   ├── auth.ts
│   │   │   ├── doctor.ts
│   │   │   ├── analysis.ts
│   │   │   └── report.ts
│   │   │
│   │   ├── views/               # 页面组件
│   │   │   ├── auth/
│   │   │   │   ├── LoginView.vue
│   │   │   │   └── RegisterView.vue
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   └── DashboardView.vue
│   │   │   │
│   │   │   ├── doctor/
│   │   │   │   ├── DoctorListView.vue
│   │   │   │   └── DoctorDetailView.vue
│   │   │   │
│   │   │   ├── analysis/
│   │   │   │   ├── ClusterAnalysisView.vue
│   │   │   │   └── AnalysisResultView.vue
│   │   │   │
│   │   │   ├── report/
│   │   │   │   ├── ReportListView.vue
│   │   │   │   ├── ReportDetailView.vue
│   │   │   │   └── ReportGenerateView.vue
│   │   │   │
│   │   │   └── admin/
│   │   │       ├── UserManageView.vue
│   │   │       └── SystemLogsView.vue
│   │   │
│   │   ├── components/          # 公共组件
│   │   │   ├── layout/
│   │   │   │   ├── MainLayout.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── Navbar.vue
│   │   │   │
│   │   │   ├── common/
│   │   │   │   ├── Loading.vue
│   │   │   │   ├── Empty.vue
│   │   │   │   └── Pagination.vue
│   │   │   │
│   │   │   ├── charts/
│   │   │   │   ├── ScatterChart3D.vue
│   │   │   │   ├── RadarChart.vue
│   │   │   │   └── TrendChart.vue
│   │   │   │
│   │   │   └── report/
│   │   │       ├── MarkdownRenderer.vue
│   │   │       └── StreamingText.vue
│   │   │
│   │   ├── composables/         # 组合式函数
│   │   │   ├── useAuth.ts
│   │   │   ├── useTable.ts
│   │   │   ├── useChart.ts
│   │   │   └── useSSE.ts
│   │   │
│   │   ├── utils/               # 工具函数
│   │   │   ├── request.ts       # Axios封装
│   │   │   ├── storage.ts       # LocalStorage
│   │   │   ├── validators.ts
│   │   │   └── formatters.ts
│   │   │
│   │   ├── types/               # TypeScript类型
│   │   │   ├── user.ts
│   │   │   ├── doctor.ts
│   │   │   ├── analysis.ts
│   │   │   └── report.ts
│   │   │
│   │   └── assets/              # 资源文件
│   │       ├── styles/
│   │       │   ├── index.scss   # 全局样式
│   │       │   ├── variables.scss
│   │       │   └── mixins.scss
│   │       │
│   │       └── images/
│   │           └── login-bg.svg
│   │
│   └── index.html
│
└── docs/                        # 文档
    ├── API.md                   # API文档
    ├── DEVELOPMENT.md           # 开发指南
    ├── DEPLOYMENT.md            # 部署指南
    └── DIFY_SETUP.md            # Dify配置指南
```

---

## 7. UI/UX设计规范

### 7.1 设计系统

#### 7.1.1 色彩体系

scss

```scss
// frontend/src/assets/styles/variables.scss

// 主色调
$primary-color:#1890FF;// 科技蓝
$primary-light:#40A9FF;
$primary-dark:#096DD9;

// 辅助色
$success-color:#52C41A;// 成功/增长
$warning-color:#FAAD14;// 警告
$danger-color:#F5222D;// 错误/下降
$info-color:#13C2C2;// 信息

// 中性色
$bg-color:#F0F2F5;// 背景
$card-bg:#FFFFFF;// 卡片背景
$border-color:#D9D9D9;// 边框

$text-primary:#262626;// 标题
$text-secondary:#595959;// 正文
$text-disabled:#8C8C8C;// 禁用/次要

// 聚类标签色
$cluster-high-value:#FF6B6B;// 高价值客户
$cluster-potential:#4ECDC4;// 潜力客户
$cluster-mass:#95E1D3;// 大众客户
```

#### 7.1.2 字体系统

scss

```scss
// 字体族
$font-family: -apple-system, BlinkMacSystemFont,'Segoe UI', 
'PingFang SC','Hiragino Sans GB','Microsoft YaHei',
              sans-serif;

// 字号
$font-size-xs:12px;
$font-size-sm:14px;
$font-size-base:16px;
$font-size-lg:18px;
$font-size-xl:20px;
$font-size-xxl:24px;

// 字重
$font-weight-normal:400;
$font-weight-medium:500;
$font-weight-bold:600;
```

#### 7.1.3 间距系统

scss

```scss
$spacing-xs:4px;
$spacing-sm:8px;
$spacing-md:16px;
$spacing-lg:24px;
$spacing-xl:32px;
$spacing-xxl:48px;
```

#### 7.1.4 圆角与阴影

scss

```scss
// 圆角
$border-radius-sm:2px;
$border-radius-base:4px;
$border-radius-lg:8px;
$border-radius-circle:50%;

// 阴影
$shadow-card:02px8pxrgba(0,0,0,0.08);
$shadow-hover:04px16pxrgba(0,0,0,0.12);
$shadow-modal:08px24pxrgba(0,0,0,0.16);
```

### 7.2 动画效果

#### 7.2.1 过渡动画

scss

```scss
// 通用过渡
$transition-base: all 0.3s ease;
$transition-fast: all 0.2s ease;
$transition-slow: all 0.5s ease;

// 使用示例
.card {
transition:$transition-base;
  
&:hover {
transform:translateY(-4px);
box-shadow:$shadow-hover;
}
}
```

#### 7.2.2 数字滚动动画

typescript

```typescript
// frontend/src/utils/animations.ts
import{CountUp}from'countup.js';

exportfunctionanimateNumber(
  element:HTMLElement, 
  endValue:number, 
  duration:number=2
){
const countUp =newCountUp(element, endValue,{
    duration,
    separator:',',
    decimal:'.',
    prefix:'',
    suffix:''
});
  
if(!countUp.error){
    countUp.start();
}
}
```

#### 7.2.3 页面过渡

vue

```vue
<!-- App.vue -->
<template>
  <router-view v-slot="{ Component }">
    <transition name="fade-slide" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
```

### 7.3 响应式设计

#### 7.3.1 断点定义

scss

```scss
$breakpoint-xs:480px;// 手机
$breakpoint-sm:768px;// 平板
$breakpoint-md:1024px;// 小屏幕电脑
$breakpoint-lg:1280px;// 普通电脑
$breakpoint-xl:1920px;// 大屏幕
```

#### 7.3.2 响应式布局

vue

```vue
<template>
  <el-container class="main-layout">
    <!-- 侧边栏在移动端折叠 -->
    <el-aside 
      :width="isMobile ? '0' : '240px'"
      :class="{ 'mobile-hidden': isMobile }"
    >
      <Sidebar />
    </el-aside>
  
    <el-container>
      <el-header>
        <Navbar @toggle-sidebar="toggleSidebar" />
      </el-header>
    
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const isMobile = ref(false);

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});
</script>
```

### 7.4 组件设计规范

#### 7.4.1 卡片组件

vue

```vue
<!-- components/common/DataCard.vue -->
<template>
  <el-card 
    class="data-card"
    :class="{ 'is-hoverable': hoverable }"
    shadow="hover"
  >
    <div class="card-header">
      <div class="icon-wrapper" :style="{ background: iconColor }">
        <component :is="icon" class="icon" />
      </div>
      <div class="card-title">{{ title }}</div>
    </div>
  
    <div class="card-content">
      <div class="main-value">{{ mainValue }}</div>
      <div class="trend" :class="trendClass">
        <el-icon><CaretTop v-if="trend > 0" /><CaretBottom v-else /></el-icon>
        {{ Math.abs(trend) }}%
      </div>
    </div>
  
    <div class="card-footer">
      <span class="label">{{ label }}</span>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  mainValue: string | number;
  trend: number;
  label: string;
  icon: any;
  iconColor?: string;
  hoverable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: '#1890FF',
  hoverable: true
});

const trendClass = computed(() => 
  props.trend > 0 ? 'trend-up' : 'trend-down'
);
</script>

<style scoped lang="scss">
.data-card {
  height: 160px;
  transition: all 0.3s ease;
  
  &.is-hoverable:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    gap: 12px;
  
    .icon-wrapper {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
    
      .icon {
        font-size: 24px;
        color: white;
      }
    }
  }
  
  .card-content {
    margin-top: 16px;
    display: flex;
    align-items: baseline;
    gap: 12px;
  
    .main-value {
      font-size: 32px;
      font-weight: 600;
      color: $text-primary;
    }
  
    .trend {
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 4px;
    
      &.trend-up {
        color: $success-color;
      }
    
      &.trend-down {
        color: $danger-color;
      }
    }
  }
  
  .card-footer {
    margin-top: 8px;
    color: $text-disabled;
    font-size: 14px;
  }
}
</style>
```

### 7.5 图表配置规范

#### 7.5.1 ECharts主题配置

typescript

```typescript
// frontend/src/utils/chartTheme.ts
exportconst chartTheme ={
  color:[
'#1890FF','#52C41A','#FAAD14','#F5222D', 
'#13C2C2','#722ED1','#EB2F96'
],
  
  backgroundColor:'transparent',
  
  textStyle:{
    fontFamily:'PingFang SC, Microsoft YaHei, sans-serif',
    fontSize:14,
    color:'#595959'
},
  
  title:{
    textStyle:{
      color:'#262626',
      fontSize:18,
      fontWeight:600
},
    subtextStyle:{
      color:'#8C8C8C',
      fontSize:14
}
},
  
  legend:{
    textStyle:{
      color:'#595959'
}
},
  
  grid:{
    left:'3%',
    right:'4%',
    bottom:'3%',
    containLabel:true
}
};
```

#### 7.5.2 3D散点图配置

typescript

```typescript
// frontend/src/utils/chartConfigs.ts
exportfunctiongetScatter3DOption(data:any[]){
return{
    title:{
      text:'医生聚类3D可视化',
      left:'center'
},
    tooltip:{
formatter:(params:any)=>{
return`
          <div style="padding: 8px;">
            <strong>${params.name}</strong><br/>
            频次: ${params.value[0]}<br/>
            金额: ${params.value[1].toLocaleString()}<br/>
            聚类: ${params.value[3]}
          </div>
`;
}
},
    grid3D:{
      viewControl:{
        autoRotate:true,
        autoRotateSpeed:5
},
      light:{
        main:{
          intensity:1.2,
          shadow:true
},
        ambient:{
          intensity:0.3
}
}
},
    xAxis3D:{
      name:'Frequency',
      type:'value'
},
    yAxis3D:{
      name:'Monetary',
      type:'log',
      logBase:10
},
    zAxis3D:{
      name:'Recency',
      type:'value'
},
    series:[{
      type:'scatter3D',
      data: data,
      symbolSize:5,
      itemStyle:{
        opacity:0.7
},
      emphasis:{
        itemStyle:{
          opacity:1,
          borderWidth:2,
          borderColor:'#fff'
}
}
}]
};
}
```

---

## 8. 开发优先级与里程碑

### Phase 1: 基础架构（第1-2周）

- [X] 后端骨架搭建
- [X] 数据库设计与数据导入
- [ ] JWT认证实现
- [ ] 前端项目初始化
- [ ] 基础路由与布局

### Phase 2: 核心功能（第3-4周）

- [ ] 医生列表与详情页
- [ ] K-Means聚类分析
- [ ] 聚类结果可视化
- [ ] Dashboard数据看板

### Phase 3: AI集成（第5-6周）

- [ ] Dify工作流配置
- [ ] AI报告生成功能
- [ ] 流式输出实现
- [ ] 知识库构建

### Phase 4: 完善与测试（第7-8周）

- [ ] 系统管理功能
- [ ] 性能优化
- [ ] 单元测试与集成测试
- [ ] 文档完善

---

## 附录：技术选型说明

### A.1 为什么选择FastAPI？

- 异步支持，高性能
- 自动生成API文档（Swagger）
- 类型提示友好
- 易于集成Dify等外部服务

### A.2 为什么选择Vue3？

- Composition API更灵活
- TypeScript支持优秀
- 生态成熟（Element Plus、ECharts）
- 学习曲线平缓

### A.3 为什么选择SQLite？

- 轻量级，易部署
- 单文件数据库，方便备份
- 适合中小规模数据（< 100GB）
- 可轻松迁移到PostgreSQL

### A.4 为什么选择Dify？

- 可视化工作流编排
- 内置RAG支持
- 工具调用机制完善
- 开源免费

---

 **文档版本** : v1.0

 **最后更新** : 2025-12-14

 **维护者** : 刘蕊
