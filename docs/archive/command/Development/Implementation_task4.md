
# Role: Python Backend Developer & Data Scientist

# Project Status Update

* **当前阶段** : 后端初始化完成，ETL 脚本已成功执行。
* **数据状态** : SQLite 数据库 (`backend/pharma.db`) 的 `doctors` 表中已存储 **738,772 条** 医生记录。每条记录均包含清洗好的 RFM (`rfm_recency`, `rfm_frequency`, `rfm_monetary`) 值。
* **下一步目标** : 开发后端的核心业务逻辑——K-Means 聚类服务，并实现配套的 RESTful API。

# Inputs

1. **Database** : `backend/pharma.db` (真实数据已就绪)
2. **Models** : `backend/app/models.py` (关注 `Doctor` 和 `ClusterResult` 模型)

# Task Description

请在 `backend/app` 目录下编写/更新以下模块，构建完整的分析服务链路。

## 1. 核心算法服务 (`backend/app/services/analysis_service.py`)

请创建一个 `AnalysisService` 类（或函数集合），实现以下关键逻辑：

* **数据加载 (Load)** :
* 使用 `pd.read_sql` 从 `doctors` 表读取 `npi` 和 RFM 三个字段。
* *注意* : 数据量约为 74万行，Pandas 处理此量级毫无压力，但需注意内存优化。
* **数据预处理 (Preprocess)** :
* **关键步骤** : 初始化 `sklearn.preprocessing.StandardScaler`。
* 对 RFM 数据进行标准化（Standardization），因为 `Monetary` (金额，可达数万) 和 `Recency` (天数，0-365) 量级差异巨大，不标准化会导致聚类失效。
* **聚类执行 (K-Means)** :
* 接收参数 `k` (int, 默认 3-5)。
* 运行 `sklearn.cluster.KMeans`。
* 获取每个医生的 `labels_`。
* **结果持久化 (Save) - 性能关键点** :
* **Step A: 更新医生表** : 将计算出的 `cluster_id` 回写到 `doctors` 表。
  * *强制要求* : 使用 **批量更新 (Batch Update)** 策略。不要对 74万行数据进行逐行 `db.commit()`。建议使用 SQLAlchemy Core 的 `connection.execute(update(...))` 或将结果转为 List of Dict 后使用 `bulk_update_mappings`。
* **Step B: 保存分析摘要** : 计算每个 Cluster 的统计指标，存入 `cluster_results` 表。
  * 统计项应包括：`avg_recency`, `avg_frequency`, `avg_monetary`, `count` (人数), `percentage` (占比)。
  * 将这些指标序列化为 JSON 字符串，存入 `kpi_summary` 字段。
  * 为 Dify AI 预留的 `ai_strategy` 字段暂时留空或填入 "Pending Generation"。

## 2. API 路由实现 (`backend/app/routers/`)

### 2.1 医生查询接口 (`routers/doctors.py`)

* `GET /api/doctors`:
  * 分页返回医生列表 (默认 `page=1`, `page_size=20`)。
  * 支持可选过滤参数 `cluster_id` (例如：只看 "高价值" 这一群医生)。
* `GET /api/doctors/{npi}`:
  * 返回单个医生的完整画像信息。

### 2.2 分析控制接口 (`routers/analysis.py`)

* `POST /api/analysis/perform`:
  * Body: `{ "k": 4 }`
  * 功能: 触发后台的 K-Means 分析服务。
  * 返回: `{ "status": "success", "message": "Clustering completed for 738,772 doctors." }`
* `GET /api/analysis/results`:
  * 功能: 获取 `cluster_results` 表中的所有记录。
  * 用途: 前端绘制雷达图的数据源。

## 3. 系统整合

* 更新 `backend/app/main.py`: 引入并注册 `doctors` 和 `analysis` 路由。

# Constraints & Best Practices

1. **依赖注入** : 所有数据库操作必须通过 `Depends(get_db)` 获取 Session。
2. **异常处理** : 如果数据库为空 (Row count = 0)，API 应返回清晰的 400 错误提示 "No data available for analysis"。
3. **类型安全** : 使用 Pydantic Schema (`schemas.py`) 定义请求和响应模型。
