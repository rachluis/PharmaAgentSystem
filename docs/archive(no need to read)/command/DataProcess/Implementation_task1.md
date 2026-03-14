# Role: Python Backend Developer & Data Scientist

# Context

项目阶段：FastAPI 后端已初始化，SQLite 数据库 (`backend/pharma.db`) 已通过 ETL 脚本填充了真实的医生画像数据 (`doctors` 表)。
当前目标：开发核心的 **K-Means 聚类分析服务** 以及配套的  **RESTful API 接口** ，以便前端能够调用算法并获取分析结果。

# Inputs

1. **Database** : `backend/pharma.db` (包含已清洗的 RFM 数据)。
2. **Models** : `backend/app/models.py` (已定义的 `Doctor` 和 `ClusterResult` 模型)。

# Task: 开发分析服务与 API

请在 `backend/app` 中完善以下模块：

## 1. 核心算法服务 (`services/analysis_service.py`)

创建一个服务类或函数集，实现以下逻辑：

* **Load Data** : 从数据库读取所有医生的 `rfm_recency`, `rfm_frequency`, `rfm_monetary` 字段。
* **Preprocess** : 使用 `sklearn.preprocessing.StandardScaler` 对 RFM 数据进行标准化处理（非常重要，因为金额和频次的量级差异巨大）。
* **K-Means Execution** :
* 接收参数 `k` (聚类数量)。
* 运行 `sklearn.cluster.KMeans`。
* **Save Results** :
* **更新医生表** ：将计算出的 label (0, 1, 2...) 回写到 `Doctor.cluster_id` 字段。
* **保存分析结果** ：计算每个簇的统计指标（平均 R/F/M 值、人数占比），并存入 `ClusterResult` 表。
  *  *提示* ：`ClusterResult.kpi_summary` 是 JSON 字段，请将统计字典序列化后存入。

## 2. API 路由实现 (`routers/`)

### 2.1 医生数据接口 (`routers/doctors.py`)

* `GET /api/doctors`: 分页获取医生列表 (参数: `page`, `page_size`)。
* `GET /api/doctors/{npi}`: 获取单个医生的详细信息（包含其 RFM 值和所属 Cluster ID）。

### 2.2 分析接口 (`routers/analysis.py`)

* `POST /api/analysis/cluster`: 触发聚类分析。
  * Body: `{ "k": 4 }`
  * Response: `{ "message": "Clustering completed", "clusters_summary": [...] }`
* `GET /api/analysis/results`: 获取当前的聚类结果统计（用于前端雷达图展示）。

## 3. 整合路由

* 修改 `backend/app/main.py`，注册以上两个新的 Router。

# Constraints

* **依赖注入** : 使用 `Depends(get_db)` 获取数据库会话。
* **异常处理** : 如果数据库为空或 K 值不合法，返回 HTTP 400 错误。
* **性能** : 对于 `Save Results` 步骤，更新几万名医生的 `cluster_id` 时，请使用批量更新 (Batch Update) 策略，避免逐行 commit。

# Output

请生成以下文件的完整代码：

1. `backend/app/services/analysis_service.py`
2. `backend/app/routers/doctors.py`
3. `backend/app/routers/analysis.py`
4. `backend/app/main.py` (修改版)
