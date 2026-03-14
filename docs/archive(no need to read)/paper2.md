# Context

我正在撰写本科毕业论文《基于多智能体协作的医药市场画像与策略生成系统》。
前三章（绪论、理论基础、需求分析）已完成初稿。
现在需要撰写 **第4章 系统实现** 和 **第5章 数据分析与实验**。

# Input Documents (必须严格基于这些文档写作)

1. **`DATA_DICTIONARY.md`**: 数据库设计细节。
2. **`system_architecture_and_workflow.md`**: 核心业务流程。
3. **`data_report.txt`**: 数据的具体统计特征（作为实验数据的来源）。
4. **`clustering_analysis_design.md`**: 聚类模块的设计细节。

# Writing Requirements (针对答辩反馈优化)

1. **拒绝宽泛**: 严禁使用“大数据的应用日益广泛”这种空话。必须具体到：“本研究处理了 CMS Open Payments 数据集中 1540 万条交易记录...”。
2. **去 AI 味**: 句式要平实、客观。多用被动语态（如“系统被设计为...”），少用排比句。
3. **数据支撑**: 涉及到字段、表名时，必须使用文档中的真实名称（如 `doctors` 表，`rfm_score` 字段）。

# Chapter Outline & Instructions

## 第4章 系统关键模块实现 (System Implementation)

*目标：展示工程落地能力，证明系统“做出来了”。*

* **4.1 数据清洗与 ETL 实现**:
  * 描述如何处理 1540 万行 CSV 数据。
  * 引用 `data_report.txt` 中的数据特征（如缺失值处理、`specialty` 字段的清洗逻辑）。
  * 核心代码逻辑：分块读取 (Chunking)、内存聚合 RFM 指标。
* **4.2 K-Means 聚类服务实现**:
  * 描述 `analysis_service.py` 的逻辑。
  * 说明数据标准化 (`StandardScaler`) 的必要性（因为 Monetary 和 Frequency 量级差异大）。
* **4.3 Dify 智能体集成实现**:
  * 描述后端如何通过 SSE (Server-Sent Events) 与 Dify 进行流式交互。
  * **重点**: 展示 System Prompt 的设计（引用 `clustering_analysis_design.md` 中的 Prompt 结构），解释如何通过 Prompt Engineering 让 AI 扮演“医药市场总监”。

## 第5章 数据分析与实验结果 (Data Analysis & Experiments)

*目标：展示数据科学能力，证明算法“算得对”。*

* **5.1 实验环境与数据准备**:
  * 说明实验硬件环境、Python 版本、Scikit-learn 版本。
  * 数据规模：最终入库的有效医生数量（738,772 人）。
* **5.2 聚类参数优化 (K值选择)**:
  * 描述使用 **肘部法则 (Elbow Method)** 和 **轮廓系数 (Silhouette Score)** 确定最佳 K 值（K=2 或 K=3）的过程。
  * 分析原因：引用 `data_report.txt` 中的数据分布（Monetary 极度右偏，长尾效应明显），解释为什么数据特征导致了这样的 K 值选择。
* **5.3 聚类结果画像分析**:
  * 详细分析 K=2（或 K=3）时各群体的特征。
  * **群体 A (核心高价值)**: R/F/M 具体数值特征，业务含义。
  * **群体 B (长尾潜力/低活)**: 特征描述。
  * *要求*: 结合医药业务场景进行解读，而非仅仅列出数字。

---

# Action

请基于上述大纲，撰写 **第4章** 和 **第5章** 的正文内容。格式为 Markdown。
