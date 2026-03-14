# 第4章 关键模块实现

本章将深入阐述系统核心功能模块的代码实现细节。系统开发遵循“高内聚、低耦合”的原则，主要包括数据处理（ETL）模块、核心算法服务模块、AI Agent 对接模块以及前端交互模块的实现。

## 4.1 数据处理 (ETL) 模块实现

数据处理是系统的基石，主要负责将原始的 CSV 格式交易记录转换为可用于算法分析的医生画像数据。

### 4.1.1 数据清洗与聚合

原始的 CMS Open Payments 数据分散在数千万条交易记录中。系统通过 Python 的 Pandas 库实现了以下关键步骤：

1. **数据加载与去重**：使用 `pandas.read_csv` 分块读取大文件，去除完全重复的记录。
2. **缺失值处理**：对于 `Total_Amount_of_Payment_USD` 字段，剔除空值或小于等于 0 的异常记录。
3. **RFM 特征聚合**：
    以 `Physician_Profile_ID` (NPI) 为分组键（Group Key），执行聚合操作：
    * **Recency**：计算 `Date_of_Payment` 的最大值与当前日期的差值。
    * **Frequency**：统计每个 NPI 下的记录行数（Count）。
    * **Monetary**：对 `Total_Amount_of_Payment_USD` 求和（Sum）。

关键代码片段如下：

```python
# 数据聚合逻辑
df_grouped = df.groupby('Physician_Profile_ID').agg({
    'Date_of_Payment': lambda x: (current_date - pd.to_datetime(x.max())).days,
    'Record_ID': 'count',
    'Total_Amount_of_Payment_USD': 'sum'
}).rename(columns={
    'Date_of_Payment': 'recency_days',
    'Record_ID': 'frequency',
    'Total_Amount_of_Payment_USD': 'monetary'
})
```

### 4.1.2 异常值处理与入库

针对聚合后 Monetary 字段存在的极值（如某医生年度总额超 9000 万美元），系统采用 **99.9% 分位数截断法**（Percentile Capping）进行处理，避免极值对后续聚类造成不可逆的偏倚。处理完成后，通过 `SQLAlchemy` ORM 框架将数据批量写入 SQLite 数据库的 `doctors` 表中。

## 4.2 核心算法服务模块实现

算法服务模块封装在 `AnalysisService` 类中，负责执行 K-Means 聚类任务。

### 4.2.1 数据预处理与标准化

在执行聚类前，必须对数据进行预处理以消除量纲影响并发掘数据的真实分布。

1. **对数变换 (Log Transformation)**：针对 Frequency 和 Monetary 的长尾分布，采用 $x' = \ln(x + 1)$ 公式进行变换，使其分布形态接近正态分布。
2. **标准化 (Standardization)**：使用 `StandardScaler` 将特征缩放至均值为 0、方差为 1 的标准正态分布，确保各维度对于距离计算的权重一致。

### 4.2.2 K-Means 聚类执行

调用 `sklearn.cluster.KMeans` 库执行聚类。为保证结果的稳定性，设置 `n_init=10`（随机初始化 10 次取最优）和 `random_state=42`。聚类完成后，将生成的 `cluster_id`更新回数据库，并计算每个簇的统计中心（Centroids）。

```python
# K-Means 核心实现
def perform_clustering(self, k: int, df: pd.DataFrame):
    # 1. 对数变换
    X = np.log1p(df[['frequency', 'monetary']].values)
    # 2. 标准化
    X_scaled = self.scaler.fit_transform(X)
    # 3. 聚类
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    return labels, kmeans.cluster_centers_
```

## 4.3 Dify 智能体工作流对接实现

系统通过 RESTful API 与 Dify 平台进行交互，实现“数据-策略”的自动化生成。

### 4.3.1 Prompt 动态组装

在发送请求前，后端会动态提取目标群组的画像数据，并组装成 JSON 上下文（Context）。例如，针对 Cluster 0，系统会提取其平均金额、核心科室等信息，并未 Dify 构造如下 Prompt 变量：

```python
context = {
    "target_group": "Cluster 0 (核心高价值)",
    "stats": {
        "avg_monetary": 10462.26,
        "avg_frequency": 43.84,
        "dominant_specialty": "Cardiology"
    },
    "instruction": "请基于以上数据，生成一份针对心内科专家的学术会议邀请策略。"
}
```

### 4.3.2 SSE 流式响应处理

为提升用户体验，解决大模型生成耗时较长的问题，后端接口 `/api/v1/reports/generate-stream` 采用了 Server-Sent Events (SSE) 技术。系统通过 Python 的生成器（Generator）实时转发 Dify 返回的数据流，使得前端能够呈现“打字机”式的渐进显示效果，避免了用户在长连接中的焦虑等待。

## 4.4 前端交互模块实现

前端基于 Vue 3 框架开发，重点实现了聚类结果的三维可视化。

### 4.4.1 3D 散点图可视化

利用 ECharts 的 `scatter3D` 组件，将 RFM 三维数据映射到三维坐标系中。

* X 轴：Recency（活跃度）
* Y 轴：Frequency（频次）
* Z 轴：Monetary（金额）
* 颜色：Cluster ID（不同群组显示不同颜色）

为了解决 70 万个点直接渲染导致的浏览器卡顿问题，前端实现了一个**随机采样算法**，仅从后端请求 2000 个代表性样本点进行渲染，既保证了可视化的分布趋势准确，又维持了页面的流畅度（FPS > 30）。

### 4.4.2 动态雷达图

为了直观对比不同群组的特征差异，实现了动态雷达图（Radar Chart）。图表能够展示各 Cluster 在 R、F、M 三个维度上的归一化得分。当用户在左侧列表点击不同 Cluster 时，雷达图会高亮显示该群组的轮廓，帮助分析师快速判断该群组是“高金低频”还是“低金高频”。

## 4.5 本章小结

本章详细描述了系统从数据底层到用户界面的实现过程。通过 Pandas 实现高效 ETL，利用 Scikit-learn 的标准化与聚类算法构建分析引擎，借助 SSE 技术实现与 Dify Agent 的流畅对话，最后通过 ECharts 的采样渲染解决了大数据可视化的性能瓶颈。这些模块的协同工作，确保了系统功能的完整性与可用性。
