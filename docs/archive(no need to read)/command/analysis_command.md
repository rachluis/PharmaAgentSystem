# Role: Senior System Architect & Data Scientist

# Context

我是项目的新手开发人员。目前项目基于 FastAPI 开发，目标是构建一个"医药市场智能分析系统"。
我已经有了原始数据的分析报告（`data_report.txt`）样本数据data_sample.csv 和初步的设计文档（`pharma_system_design.md`）。
但我现在对**后端数据结构**、**核心字段的业务含义**以及**API的具体定义**感到模糊。

# Files Provided

1. `data_report.txt`: 包含 CMS Open Payments 原始数据的字段清单和统计信息。
2. `pharma_system_design.md`: 系统整体架构设计。

# Task 1: 核心数据字段分析 (Data Analysis)

请仔细阅读 `data_report.txt`，针对 **"医生画像 (Doctor Profiling)"** 和 **"K-Means 聚类 (RFM模型)"** 这两个核心目标，从 90 多个字段中挑选出最关键的字段。
请生成一个 Markdown 表格，包含以下列：

* **原始字段名 (CSV Header)**: `data_report.txt` 中的准确名称。
* **推荐后端字段名 (Snake Case)**: 在 Python 代码中应该叫什么（例如 `Total_Amount_of...` -> `total_amount`）。
* **数据类型**: Python/SQL 类型。
* **业务含义**: 该字段代表什么？
* **入选理由**: 为什么对 RFM 模型或画像分析至关重要？（例如：这是 M 值的基础，或这是聚类的分组依据）。

# Task 2: 后端 Pydantic 模型设计 (Schema Design)

基于 Task 1 选出的字段，请为 FastAPI 后端设计 Pydantic 模型 (`schemas.py` 代码)。
要求：

1. 创建一个 `PaymentRecordBase` 类。
2. 为每个字段添加 `Field(..., description="...")`，详细说明字段含义。
3. 添加 `@field_validator`：
   * 例如：验证金额 `amount` 必须大于等于 0。
   * 例如：验证 `npi` 必须是字符串且长度符合标准（如果知道标准的话）。

# Task 3: 核心 API 接口定义 (API Specification)

请根据系统架构，详细定义以下两个核心接口的 Swagger/OpenAPI 规格。请以 Markdown 格式展示，这就好比是 Swagger 文档的预览。

### 接口 A: 执行聚类分析

* **Method/URL**: `POST /api/run-clustering`
* **功能**: 触发 K-Means 算法对医生数据进行分群。
* **Request Body (JSON)**: 前端需要传什么参数？（例如：`k` 值范围、是否覆盖旧数据等）。请给出 JSON 示例。
* **Response (JSON)**: 后端返回什么？（例如：聚类中心的统计数据、各簇的人数占比）。请给出包含模拟数据的 JSON 示例。

### 接口 B: AI 策略对话

* **Method/URL**: `POST /api/chat`
* **功能**: 用户针对某个聚类结果提问，AI 返回策略。
* **Request Body (JSON)**: 包含用户的问题、当前的 Cluster ID、选中的聚类特征数据。
* **Response (JSON)**: AI 的回答内容、思考过程（可选）。

# Output Requirement

请输出为一份完整的 Markdown 技术文档，结构清晰，可以直接作为项目的 "Developer Guide" 使用。
