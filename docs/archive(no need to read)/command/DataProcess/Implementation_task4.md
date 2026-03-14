
# Role: Python Data Scientist & Backend Developer

# Project Context

* **数据状态** : SQLite (`backend/pharma.db`) 已有 73.8万 真实医生数据。
* **目标** : 完成 K-Means 聚类分析。为了方便论文写作和参数调优，我们决定**先在 Jupyter Notebook 中进行实验，确认算法效果后，再移植到后端服务中。**

# Task A: Jupyter Notebook 实验 (论文素材生成)

请在 `backend/notebooks/` 目录下创建一个 `clustering_experiment.ipynb`。
请编写代码实现以下完整的分析流程（每一步都需要可视化）：

## 1. 数据加载与探查

* 连接 SQLite 数据库，读取 `doctors` 表的 `rfm_recency`, `rfm_frequency`, `rfm_monetary` 字段。
* **可视化** : 绘制 R, F, M 三个指标的直方图 (Histogram)，展示数据分布（检查是否需要对数变换）。

## 2. 数据预处理

* 处理异常值（如金额特别大的离群点）。
* **标准化** : 使用 `StandardScaler`。
* **可视化** : 绘制标准化前后的对比图。

## 3. K 值选择 (核心论文素材)

* 使用  **肘部法则 (Elbow Method)** : 计算 K=2 到 K=8 的 SSE (误差平方和)，绘制折线图。
* 使用  **轮廓系数 (Silhouette Score)** : (由于数据量大，建议采样 1万条数据计算) 绘制 K 值对应的分数图。
* **结论** : 根据图表自动推荐一个最佳 K 值。

## 4. 聚类结果分析

* 使用最佳 K 值运行 K-Means。
* **可视化 (3D/2D)** :
* 绘制 3D 散点图 (X=R, Y=F, Z=M)，不同 Cluster 用不同颜色。
* 绘制  **雷达图 (Radar Chart)** : 展示每个 Cluster 的中心点特征（归一化后的 R/F/M）。
* **业务解读** : 打印每个 Cluster 的业务含义（例如：“Cluster 0: 高频低额 - 潜力客户”）。

# Task B: 后端服务封装 (工程落地)

在 Notebook 实验成功后，请将核心逻辑封装到 `backend/app/services/analysis_service.py` 中。

## 1. `AnalysisService` 类

* 方法 `perform_clustering(k: int)`:
  * 读取数据 -> 标准化 -> K-Means -> **批量更新数据库** (`doctors.cluster_id`)。
  * 计算并保存统计摘要到 `cluster_results` 表。

## 2. API 接口 (`routers/analysis.py`)

* `POST /api/analysis/perform`: 调用上述服务。
* `GET /api/analysis/results`: 返回雷达图所需数据。

# Output Requirements

请先生成 `clustering_experiment.ipynb` 的代码块（我会复制到 Notebook 中运行），然后再生成后端服务的代码。
