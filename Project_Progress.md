# 项目进展与开发路线图 (Project Progress & Roadmap)

 **项目名称** : 基于多智能体的医药市场画像与策略生成系统
 **当前阶段** : Phase 3 - 前后端联调与前端开发 (In Progress)
 **最后更新** : 2025-12-13

## 1. 项目概况与状态 (Status Overview)

### ✅ 已完成工作 (Completed)

1. **后端架构** : FastAPI + SQLite 骨架搭建完毕，数据库模型 (Models) 已定义。
2. **数据库设计与部署** : SQLite 数据库 (`pharma.db`) 初始化，包含医生画像、支付记录、聚类结果三张核心表。
3. **核心数据 ETL** : 编写并执行了高性能 ETL 脚本，成功处理 1540 万行 CMS 原始数据。
4. **数据入库** : **738,772 名** 医生的 RFM 画像数据已清洗并存入数据库，数据质量验证通过。
5. **算法实验** : Jupyter Notebook 完成 K-Means 建模，确认 **K=2** (或 K=3 用于演示) 为最佳聚类数。 *发现* : 数据呈极端长尾分布 (Monetary Skewness > 500)。
6. **核心服务封装** : `analysis_service.py` 已实现聚类逻辑与数据库回写。
7. **API 接口** : `/api/analysis/perform` (POST) 和 `/api/analysis/results` (GET) 已开发。

### 🚧 进行中 (In Progress)

* **[Current Action]** 前端与后端联调 (Task 6).
* **[Next]** 聚类分析页面的图表 (ECharts) 开发.
* **[Next]** AI 策略生成对接.
* **[Medium]** Dify 智能体工作流配置。

## 2. 技术架构与文件结构 (Technical Architecture)

### 2.1 当前文件结构

```
PharmaAgentSystem/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # SQLite 数据库连接
│   │   ├── models.py        # SQLAlchemy 模型 (Doctor, PaymentRecord, ClusterResult)
│   │   ├── schemas.py       # Pydantic 验证模型
│   │   ├── services/        # [待新建] 业务逻辑层
│   │   │   └── analysis_service.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── doctors.py   # [待新建] 医生查询接口
│   │       └── analysis.py  # [待新建] 分析控制接口
│   ├── scripts/
│   │   ├── etl_process.py   # 数据清洗与导入脚本 (已执行)
│   │   └── README.md
│   ├── notebooks/           # [待新建] 数据分析实验区
│   │   └── clustering_experiment.ipynb
│   ├── requirements.txt
│   └── pharma.db            # SQLite 数据库文件 (约 100MB+)
└── frontend/                # [待初始化] Vue3 前端
```

### 2.2 核心依赖 (Dependencies)

* **Web Framework** : `fastapi>=0.100.0`, `uvicorn[standard]>=0.22.0`
* **Data Science** : `pandas>=2.0.0`, `scikit-learn>=1.3.0`
* **Database** : `SQLAlchemy>=2.0.0`
* **Utils** : `python-multipart`, `tqdm` (用于进度条)

### 2.3 前端技术栈 (Frontend Tech Stack)

* **Framework** : Vue 3 (Composition API)
* **Build Tool** : Vite
* **Language** : TypeScript
* **UI Library** : Element Plus (医疗/B端风格)
* **Charts** : Apache ECharts 5
* **HTTP Client** : Axios
* **State Management** : Pinia

## 3. 数据库模型设计 (Database Schema)

| 表名                          | 主键                | 核心字段                                                                        | 用途                               |
| ----------------------------- | ------------------- | ------------------------------------------------------------------------------- | ---------------------------------- |
| **`doctors`**         | `npi`(Str)        | `rfm_recency`,`rfm_frequency`,`rfm_monetary`,`specialty`,`cluster_id` | 存储医生聚合画像，核心分析表。     |
| **`payment_records`** | `id`(Int)         | `npi`,`amount`,`payment_date`,`payment_type`                            | 存储清洗后的原始流水（可选存储）。 |
| **`cluster_results`** | `cluster_id`(Int) | `kpi_summary`(JSON),`ai_strategy`(Text),`size_count`                      | 存储 K-Means 聚类结果和 AI 策略。  |

## 4. 数据处理成果报告 (ETL Execution Report)

 **执行时间** :2025-12-13 17:11 - 17:25 (约 14 分钟)
 **数据源** : CMS Open Payments (`E:\毕设\OP_DTL_GNRL_PGYR2024_P06302025_06162025.csv`)

### 4.1 处理统计

* **原始数据行数** : 15,397,627 行
* **入库医生数 (NPI)** : **738,772 人**
* **医生画像统计** :
* **平均互动频次 (F)** : 15.82 次
* **平均总金额 (M)** : $3,377.92
* **中位数金额** : $173.92 (显示数据长尾分布明显)
* 中位数Frequency：4次

  **RFM 值范围**
* **Recency** : 2024-01-01 至 2024-12-31
* **Frequency** : 医生平均接受 15.82 次支付
* **Monetary** : 医生平均累计金额 $3,377.92

### 4.2 清洗策略实施情况

1. **过滤规则** : 仅保留 `Physician` 类型，成功剔除 `Teaching Hospital`。
2. **缺失处理** : 剔除无 NPI 的记录 (约 0.31%)。
3. **RFM 聚合** : 内存计算成功，未出现内存溢出 (Out of Memory)。
4. ETL Script 功能

 **文件** :backend/scripts/etl_process.py

 **核心功能** :

* Chunked CSV 读取 (50k 行/批次)
* 过滤: 仅保留 Physician, 排除 Teaching Hospital
* 清洗: 日期转换, 金额验证
* RFM 聚合: 内存中计算 Recency/Frequency/Monetary
* 批量插入: 使用 SQLAlchemy bulk operations

### 4.3 核心保留字段

* 已从 91 个原始字段中提取以下 11 个关键字段用于后续建模：
* `Covered_Recipient_NPI`, `First_Name`, `Last_Name`
* `Specialty`, `State` (地理维度)
* `Total_Amount` (M), `Date_of_Payment` (R), `Nature_of_Payment`

### 4.4 数据质量验证

✅  **数据库验证** : 738,772 条医生记录成功插入 ✅  **RFM 计算** : 所有医生均有 R/F/M 值 ✅  **数据完整性** : NPI 主键唯一,无重复

### 4.5 示例数据

 **Top 5 医生 (按 Monetary 排序)** :

1. NPI: 1821157041, Name: CHARLES GOODIS, Specialty: Orthopaedic Surgery
2. NPI: 1366487498, Name: STEPHEN BURKHART, ...

**Task A & B 已完成!**

 **1. Jupyter Notebook 实验** :

* 已创建:

  ```
  backend/notebooks/clustering_experiment.ipynb
  ```

* 包含: 数据加载 -> RFM 可视化 -> 预处理 -> K 值选择 (Elbow/Silhouette) -> 3D 聚类图 -> 雷达图 -> 业务解读。
* **使用** : 您可以在 VS Code 中直接打开此文件运行。

 **2. 后端服务封装** :

* **Service** :

```
  backend/app/services/analysis_service.py
```

* 实现了

  ```
  perform_clustering()
  ```

  方法，包含自动数据库更新和策略生成。
* **API Router** :

```
  backend/app/routers/analysis.py
```

```
POST /api/analysis/perform
```

: 触发聚类分析。

```
GET /api/analysis/results
```

: 获取分析结果。

### 4.6 核心数据资产 (Data Assets)

### 4.6.1 聚类结果示例 (K=2)

* **Cluster 0 (核心组)** : ~31.6万人，平均金额 $7,713，互动频次高。
* **Cluster 1 (大众组)** : ~42.2万人，平均金额 $126，互动频次低。

### 4.6.2 API 接口定义

* `POST /api/analysis/perform`: 触发聚类，更新数据库。
* `GET /api/analysis/results`: 获取用于前端绘图的 JSON 数据。

## 5. 下一步开发计划 (Next Steps)

### Task 4:  API 开发 (当前重点)

* **4.2 后端服务封装** :
* 将实验成功的代码移植到 `app/services/analysis_service.py`。
* 实现 `perform_clustering(k)` 函数，支持结果回写数据库。
* **4.3 API 接口实现** :
* `GET /api/doctors`: 分页查询医生列表。
* `POST /api/analysis/perform`: 触发聚类任务。
* `GET /api/analysis/results`: 获取聚类统计结果。

### Task 5: 前端初始化与基础开发

1. **初始化** : 创建 `frontend` 目录，安装依赖。
2. **配置** : 设置 Vite 代理 (解决跨域)，封装 Axios。
3. **开发** :

* **Layout** : 侧边栏 + 顶部导航。
* **Dashboard** : 概览页。
* **Analysis View** : 聚类分析页 (核心)。

### Task 6: 前端与后端联调

* 在前端页面点击“开始分析”按钮，调用后端 API，展示 Loading 动画，完成后渲染雷达图和散点图。

### Task 7: AI Agent 集成

* 配置 Dify 知识库和工作流。
* 编写 Prompt：基于 `cluster_results` 表中的 JSON 数据生成营销策略。
