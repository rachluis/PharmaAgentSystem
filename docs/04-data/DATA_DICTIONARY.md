# 数据字典与前后端映射文档 (Data Dictionary)

**版本**: 1.0
**最后更新**: 2025-12-16
**对应后端**: `backend/app/models.py`
**前端规范**: 字段名保持 **snake_case** (下划线命名) 以与后端 API 响应保持一致。

---

## 1. 数据库模型概览

系统包含 7 张核心数据表，用于支撑用户认证、医生画像、数据分析与 AI 策略生成。

| 表名 (Table)              | 模型类 (Model)    | 用途描述                                             | 关键关联               |
| :------------------------ | :---------------- | :--------------------------------------------------- | :--------------------- |
| **users**           | `User`          | 用户认证、权限管理与个人信息                         | 关联任务、报告、日志   |
| **doctors**         | `Doctor`        | **(核心)** 医生基础信息、RFM计算结果、聚类标签 | 关联支付记录、聚类结果 |
| **payment_records** | `PaymentRecord` | 原始支付/交易流水 (清洗后)                           | 属于医生               |
| **cluster_results** | `ClusterResult` | K-Means 聚类分析产出的统计结果与可视化数据           | 包含多名医生           |
| **analysis_tasks**  | `AnalysisTask`  | 异步分析任务的状态跟踪 (进度、状态)                  | 关联用户、聚类结果     |
| **ai_reports**      | `AIReport`      | Dify 生成的市场策略报告 (Markdown)                   | 关联聚类或医生         |
| **system_logs**     | `SystemLog`     | 系统操作审计日志                                     | 关联用户               |

---

## 2. 详细字段映射表

### 2.1 Doctors 表 (核心画像)

* **API 路径**: `/api/v1/doctors`
* **前端组件参考**: `DoctorList.vue`, `DoctorDetail.vue`

| 后端字段 (DB Column) | 数据类型     | 前端显示名称 (Label) | 前端属性名 (Prop) | 备注/约束 (Notes)                         |
| :------------------- | :----------- | :------------------- | :---------------- | :---------------------------------------- |
| `npi`              | String (PK)  | NPI 编号             | `npi`           | 唯一主键，10位数字字符串                  |
| `full_name`        | String       | 医生姓名             | `full_name`     | 冗余字段 (`first_name` + `last_name`) |
| `specialty`        | String       | 专业领域             | `specialty`     | 如 "Cardiology", "Dentist"                |
| `state`            | String       | 州                   | `state`         | 2位大写简写 (如 CA, NY)                   |
| `city`             | String       | 城市                 | `city`          |                                           |
| `rfm_monetary`     | Float        | 总金额               | `rfm_monetary`  | **KPI指标**: 累计支付总额 ($)       |
| `rfm_frequency`    | Integer      | 频次                 | `rfm_frequency` | **KPI指标**: 支付记录总数           |
| `recency_days`     | Integer      | 最近支付间隔         | `recency_days`  | **KPI指标**: 距今天数 (越小越活跃)  |
| `cluster_id`       | Integer (FK) | 分群 ID              | `cluster_id`    | 0, 1, 2, 3...                             |
| `cluster_label`    | String       | 客户分群             | `cluster_label` | 业务标签 (如"核心客户")                   |
| `updated_at`       | DateTime     | 更新时间             | `updated_at`    |                                           |

### 2.2 Users 表

| 后端字段       | 数据类型 | 前端显示名称 | 前端属性名     | 备注                               |
| :------------- | :------- | :----------- | :------------- | :--------------------------------- |
| `username`   | String   | 用户名       | `username`   | 登录账号                           |
| `full_name`  | String   | 姓名         | `full_name`  | 显示名称                           |
| `role`       | String   | 角色         | `role`       | `admin`, `analyst`, `viewer` |
| `avatar_url` | String   | 头像         | `avatar_url` | 图片 URL                           |
| `is_active`  | Boolean  | 状态         | `is_active`  | `true` 为启用                    |

### 2.3 ClusterResults 表 (聚类结果)

前端通常通过 `visualization_data` 字段渲染图表。

| 后端字段               | 数据类型 | 前端显示名称 | 前端属性名             | 备注                     |
| :--------------------- | :------- | :----------- | :--------------------- | :----------------------- |
| `cluster_name`       | String   | 分群名称     | `cluster_name`       |                          |
| `size_count`         | Integer  | 群体人数     | `size_count`         | 该群组包含的医生数       |
| `size_percentage`    | Float    | 占比         | `size_percentage`    | 0.0 - 1.0 (或百分比)     |
| `kpi_summary`        | JSON     | 关键指标     | `kpi_summary`        | 含 Avg_M, Avg_F 等统计值 |
| `visualization_data` | JSON     | 图表数据     | `visualization_data` | ECharts 渲染用数据       |
| `strategy_focus`     | String   | 策略重心     | `strategy_focus`     | 短句或是 Dify 生成的摘要 |
| `context_for_llm`    | String   | AI 上下文    | `context_for_llm`    | 传递给 LLM 的原始数据    |

### 2.4 AIReports 表 (AI 报告)

| 后端字段               | 数据类型 | 前端显示名称 | 前端属性名             | 备注                     |
| :--------------------- | :------- | :----------- | :--------------------- | :----------------------- |
| `report_title`       | String   | 报告标题     | `report_title`       |                          |
| `report_type`        | String   | 报告类型     | `report_type`        | `cluster_strategy` 等    |
| `report_content`     | Text     | 内容         | `report_content`     | Markdown 格式            |
| `report_summary`     | Text     | 摘要         | `report_summary`     |                          |
| `dify_conversation_id`| String  | 会话 ID      | `dify_conversation_id`| Dify 平台返回的 ID       |
| `generation_time`    | Float    | 生成耗时     | `generation_time`    | 秒                       |
| `status`             | String   | 状态         | `status`             | `published`/`draft`    |

---

## 3. API 接口规范摘要

基于 RESTful 风格，所有接口前缀为 `/api/v1`。

### 3.1 医生管理 (Doctors)

* `GET /doctors` - 分页获取医生列表 (支持筛选: specialty, state, cluster_id)
* `GET /doctors/{npi}` - 获取医生详细画像
* `GET /doctors/statistics` - 获取全局统计数据 (已集成服务端缓存)

### 3.2 认证 (Auth)

* `POST /auth/login` - 登录 (返回 JWT Token)
* `POST /auth/register` - 注册
* `GET /auth/me` - 获取当前用户信息

### 3.3 分析任务 (Analysis)

* `POST /analysis/tasks` - 创建并启动新的分析任务
* `GET /analysis/tasks` - 获取任务列表
* `DELETE /analysis/tasks/{id}` - 删除任务

### 3.4 聚类结果 (Cluster Results)

* `GET /analysis/tasks/results/list` - 获取所有聚类结果详情 (包含 AI 策略摘要)

### 3.5 AI 报告 (AI Reports)

* `POST /reports/generate-stream` - **SSE** 流式生成报告
* `GET /reports` - 报告列表
* `GET /reports/{id}` - 报告详情
* `DELETE /reports/{id}` - 删除报告
