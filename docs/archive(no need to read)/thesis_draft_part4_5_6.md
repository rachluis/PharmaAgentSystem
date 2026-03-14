# 第4章 关键模块实现

本章详细阐述系统的核心功能模块代码实现，重点介绍数据处理 ETL、聚类分析引擎、Dify 智能体对接服务以及前端可视化交互的编码逻辑。

## 4.1 数据处理 (ETL) 模块实现

数据处理模块负责将非结构化的原始交易流水转化为结构化的医生画像数据。该过程主要通过 Python 脚本 `clean_data.py` 和 `DataInput.py` 实现。

### 4.1.1 数据加载与清洗

利用 Pandas 库读取 CMS Open Payments 发布的 CSV 源文件。由于数据量庞大（1,540 万条），采用分块读取或指定列类型的方式优化内存占用。清洗逻辑包括：

1. **缺失值处理**：剔除 `Physician_NPI` 为空的无效记录。
2. **异常值过滤**：过滤掉金额为负数（退款记录）或金额极小（< $1）的噪声数据。
3. **数据聚合**：按 `Physician_NPI` 进行 GroupBy 操作，聚合计算以下指标：
    * `Total_Amount_of_Payment_USD` 求和 -> `rfm_monetary`
    * `Record_ID` 计数 -> `rfm_frequency`
    * `Date_of_Payment` 最大值 -> `last_payment_date`

```python
# 核心聚合逻辑示例
df_grouped = df.groupby('Physician_NPI').agg({
    'Total_Amount_of_Payment_USD': 'sum',
    'Record_ID': 'count',
    'Date_of_Payment': 'max'
}).reset_index()
```

## 4.2 聚类分析服务实现

聚类分析服务封装在后端 `AnalysisService` 类中，位于 `backend/app/services/analysis_service.py`。该服务实现了从数据加载、预处理到模型训练的全流程。

### 4.2.1 特征工程

针对医药支付数据典型的长尾分布特征（部分医生金额极高，大部分极低），在进行 K-Means 聚类前，必须进行对数变换（Log Transformation）以降低数据的偏度，随后使用 `StandardScaler` 进行标准化。

```python
# backend/app/services/analysis_service.py 核心代码片段
# Log transform for skewed features
for f in features:
    if f in ['frequency', 'monetary']:
        col_name = f"{f}_log"
        # 使用 log1p (log(1+x)) 避免 log(0) 错误
        df_clean[col_name] = np.log1p(df_clean[f])
        model_features.append(col_name)

# Standardization
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_clean[model_features])
```

### 4.2.2 K-Means 模型训练

使用 `sklearn.cluster.KMeans` 类执行聚类。为避免陷入局部最优，设置 `n_init=10` 让算法随机初始化 10 次并取最优结果。

```python
kmeans = KMeans(
    n_clusters=k,       # 用户前端传入的 K 值
    random_state=42,    # 固定随机种子保证结果可复现
    n_init=10,
    max_iter=300
)
cluster_labels = kmeans.fit_predict(X_scaled)
```

### 4.2.3 启发式标签生成

系统内置了 `_generate_label` 和 `_generate_strategy_rule` 方法，基于聚类中心与全局均值的对比，自动为群组打上“VIP”、“成长型”或“低活跃”的标签，为 Dify 提供初步的语义输入。

## 4.3 Dify 智能体对接服务实现

`DifyService` 类（`backend/app/services/dify_service.py`）负责与 Dify 平台进行通信。

### 4.3.1 SSE 流式通信

为了提升用户体验，避免用户在生成长篇策略报告时长时间等待，后端采用 SSE（Server-Sent Events）协议流式传输 Dify 的响应。使用 `httpx` 异步客户端调用 Dify 的 Chatflow API。

```python
# backend/app/services/dify_service.py
async def stream_chat(self, cluster_stats: str, user_intent: str):
    payload = {
        "inputs": {
            "cluster_data": cluster_stats,
            "user_focus": user_intent
        },
        "response_mode": "streaming",
        "user": "sys_admin"
    }
    # 异步流式请求
    async with client.stream("POST", f"{self.api_url}/chat-messages", json=payload) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                # 解析 SSE 数据包并 yield 给前端
                yield data["answer"]
```

## 4.4 前端可视化实现

前端 `Analysis.vue` 组件基于 Vue 3 和 ECharts 实现。特别是 3D 散点图，通过 `z` 轴（Monetary）、`x` 轴（Recency）、`y` 轴（Frequency）的三维映射，直观展示聚类效果。

```javascript
// ECharts 3D Scatter 配置
option = {
    xAxis3D: { name: 'Recency (Days)' },
    yAxis3D: { name: 'Frequency' },
    zAxis3D: { name: 'Monetary ($)' },
    series: [{
        type: 'scatter3D',
        data: this.points, // 后端返回的采样点数据
        itemStyle: {
            color: (params) => colorMap[params.data.cluster]
        }
    }]
}
```

---

# 第5章 数据分析与系统测试

本章基于系统实际运行产生的数据进行实验分析，验证系统的功能有效性与策略生成的质量。

## 5.1 数据准备与清洗结果

实验数据来源于 CMS 发布的 2024 年度 Open Payments 数据集。

* **原始数据量**：15,409,832 条交易记录。
* **清洗后数据**：738,773 条有效医生画像记录。
* **数据完整性**：所有画像记录均包含完整的 R、F、M 特征值。非空检查通过率 100%。

## 5.2 聚类效果分析

### 5.2.1 聚类参数选择

通过多次实验对比 Inertia（簇内平方和）与 Silhouette Score（轮廓系数），最终确定 **K=3** 为当前数据集下的最优聚类数。在该参数下，能够区分出业务特征明显的独立群体，且计算耗时在可接受范围内。

### 5.2.2 群体特征分析

执行 K-Means (K=3) 后，得到如下三个典型群体：

| 此处为表格 | Cluster 0 (VIP) | Cluster 1 (潜力型/成长型) | Cluster 2 (低活跃/普通) |
| :--- | :--- | :--- | :--- |
| **人数占比** | **31.1%** | 24.5% | 44.4% |
| **平均频次 (F)** | **43.84** | 1.67 | 3.99 |
| **平均金额 (M)** | **$10,462** | $156 | $192 |
| **标签定义** | **核心高价值客户** | 潜力客户 | 长尾/低效客户 |

*数据解读*：

* **Cluster 0** 仅占 31% 的人数，但具有极高的平均互动频次（43 次/年）和平均金额（$1 万+），符合“二八定律”，是药企需要重点维护的核心资产。
* **Cluster 1 & 2** 虽然人数众多（合计近 70%），但单体价值较低。其中 Cluster 1 虽然金额低但有一定的人数规模，可作为后续转化的潜力池。

## 5.3 智能策略生成实验

以 Cluster 0 (VIP) 群体数据为输入，触发 Dify 智能体进行策略生成。

**输入 Prompt 上下文**：

```json
{
  "cluster_name": "Cluster 0",
  "avg_monetary": 10462.26,
  "avg_frequency": 43.84,
  "size_percentage": 31.1
}
```

**系统生成报告摘要（截取）**：
> **策略重心**：深度维护与学术共建
>
> 1. **学术合伙人计划**：鉴于该群体高频互动的特征（年均 43 次），建议邀请其担任区域卫星会主席或 Advisory Board 成员，强化其学术身份。
> 2. **合规风险提示**：该群体涉及金额较大，需严格审查讲课费支付标准，确保所有支付均有 FMV（公允市场价值）文档支持，避免合规风险。

**评价**：
生成的策略报告准确捕捉了“高频高价值”的特征，给出的建议从单纯的“拜访”升级为“学术合作”，并敏锐地提示了高活客户的合规风险，达到了辅助资深市场经理进行决策的水平。

## 5.4 系统性能测试

在 Intel i7, 16GB RAM 的测试环境下：

* **聚类响应时间**：处理 73 万条数据，从请求发出到结果返回平均耗时 **58 秒**（包含数据库读写），满足“60 秒以内”的非功能性需求。
* **报告生成速度**：Dify 流式输出首字响应时间 < 2 秒，完整报告生成约 15-20 秒，交互体验流畅。

---

# 第6章 总结与展望

## 6.1 全文总结

本文针对医药企业数字化转型的迫切需求，设计并实现了一套基于多智能体协作的医药市场画像与策略生成系统。主要成果如下：

1. **构建了医药细分领域的 RFM 画像体系**：基于 CMS 大数据完成了 73 万名医生的全量画像，验证了对数变换在处理医药长尾数据中的有效性。
2. **验证了“算法+大模型”的协作范式**：通过 K-Means 完成客观的数据分层，再由 LLM Agent 完成主观的策略生成，成功贯通了从“数据”到“决策”的链路。
3. **实现了高可用性的原型系统**：基于 FastAPI 和 Vue 3 开发的系统具备了完整的业务流程，且通过了性能测试与实证分析。

## 6.2 研究不足

1. **数据维度单一**：目前仅使用了支付数据，缺乏处方数据（Rx）与患者疗效数据，画像维度尚不够立体。
2. **聚类算法基础**：K-Means 假设簇为凸形，对于分布形状复杂的医生群体可能存在划分偏差，未来可引入 DBSCAN 或高斯混合模型（GMM）。

## 6.3 展望

未来工作将集中在引入更多维度的数据源（如 NPI 执业数据），并探索多智能体（Multi-Agent）之间的对抗演练——即引入“合规官 Agent”与“销售 Agent”进行博弈，以生成更具鲁棒性和安全性的市场策略。
