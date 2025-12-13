
# Role: 首席技术架构师兼全栈工程师

**项目名称:** 基于多智能体的医药市场画像与策略生成系统
**目标:** 严格遵循我提供的《Development_Plan.md》和《data_report.txt》中的数据逻辑，从零开始搭建项目。

# Inputs

1. **《Development_Plan.md》** ：整体开发计划。
2. **《data_report.txt》** ：原始 CMS Open Payments 数据的真实体检报告。
3. **《analysis_assumptions.md》** ：我根据 data_report.txt 确认的  **RFM 特征选取、清洗策略、和 AI 报告数据结构** 。

# Task 1: 确认数据处理和特征工程 (Review)

请根据《data_report.txt》和我提供的《analysis_assumptions.md》中关于  **NPI 过滤** 、 **Recipent Type 过滤** 、**日期转换** 和 **RFM 聚合** 的精确策略，确认你已完全理解数据处理的复杂性。

# Task 2: 后端项目初始化 (Python FastAPI)

请立即开始执行《Development_Plan.md》中的 **阶段二** 和  **阶段三（部分）** ：

1. **目录结构** ：创建 `backend` 和 `frontend` 目录及所有子目录。
2. **后端环境** ：初始化 `backend` 目录，生成 `requirements.txt` (包含 `fastapi`, `uvicorn`, `pandas`, `scikit-learn`, `SQLAlchemy`)。
3. **数据库模型** ：在 `backend/app/models.py` 中，根据《系统设计文档》和本次分析，定义 SQLite 数据库模型：

* **Doctor (医生表)** ：存储医生基本信息和最终的 `cluster_id`。
* **PaymentRecord (支付记录表)** ：存储原始数据清洗后的核心字段（NPI, Amount, Date, Payment Type）。
* **ClusterResult (聚类结果表)** ：存储聚类中心点和 AI 所需的 JSON 摘要。

**请先给出目录结构和 `requirements.txt`，然后编写 `backend/app/models.py` 的代码。**
