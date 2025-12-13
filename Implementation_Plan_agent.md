# 后端项目初始化与数据库模型设计

根据

DataProcess.md 的 Task 2 要求，基于

data_report.txt (1540 万行 CMS Open Payments 数据) 和

analysis_assumptions.md (RFM 模型策略)，初始化后端项目并设计数据库模型。

## User Review Required

IMPORTANT

 **核心字段选择** ：从 91 列中筛选出以下核心字段用于 RFM 分析。请确认是否遗漏关键字段或需要调整。

**保留字段清单** (基于 data_report.txt 分析):

| 字段名                                                            | 用途         | 备注                     |
| ----------------------------------------------------------------- | ------------ | ------------------------ |
| `Covered_Recipient_NPI`                                         | 医生唯一标识 | 0.31% 缺失，作为聚合主键 |
| `Covered_Recipient_First_Name`                                  | 医生姓名     | 用于展示                 |
| `Covered_Recipient_Last_Name`                                   | 医生姓名     | 用于展示                 |
| `Covered_Recipient_Primary_Type_1`                              | 医生类型     | 0.22% 缺失               |
| `Covered_Recipient_Specialty_1`                                 | 专科分类     | 386 种唯一值             |
| `Recipient_State`                                               | 所在州       | 用于地理分析             |
| `Total_Amount_of_Payment_USDollars`                             | 支付金额     | **M 值核心**       |
| `Date_of_Payment`                                               | 支付日期     | **R 值核心**       |
| `Nature_of_Payment_or_Transfer_of_Value`                        | 支付类型     | 16 种类型                |
| `Applicable_Manufacturer_or_Applicable_GPO_Making_Payment_Name` | 药企名称     | 用于画像                 |
| `Name_of_Drug_or_Biological_or_Device_or_Medical_Supply_1`      | 产品名称     | 8.75% 缺失               |

---

## Proposed Changes

### Backend Directory Structure

创建以下目录结构：

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk1">PharmaAgentSystem/</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk1">├── backend/</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk1">│   ├── app/</span></div></div><div class="code-line" data-line-number="4" data-line-start="4" data-line-end="4"><div class="line-content"><span class="mtk1">│   │   ├── __init__.py</span></div></div><div class="code-line" data-line-number="5" data-line-start="5" data-line-end="5"><div class="line-content"><span class="mtk1">│   │   ├── main.py          # FastAPI 入口</span></div></div><div class="code-line" data-line-number="6" data-line-start="6" data-line-end="6"><div class="line-content"><span class="mtk1">│   │   ├── config.py        # 配置管理</span></div></div><div class="code-line" data-line-number="7" data-line-start="7" data-line-end="7"><div class="line-content"><span class="mtk1">│   │   ├── database.py      # 数据库连接</span></div></div><div class="code-line" data-line-number="8" data-line-start="8" data-line-end="8"><div class="line-content"><span class="mtk1">│   │   ├── models.py        # SQLAlchemy 模型</span></div></div><div class="code-line" data-line-number="9" data-line-start="9" data-line-end="9"><div class="line-content"><span class="mtk1">│   │   ├── schemas.py       # Pydantic 模型</span></div></div><div class="code-line" data-line-number="10" data-line-start="10" data-line-end="10"><div class="line-content"><span class="mtk1">│   │   └── routers/</span></div></div><div class="code-line" data-line-number="11" data-line-start="11" data-line-end="11"><div class="line-content"><span class="mtk1">│   │       ├── __init__.py</span></div></div><div class="code-line" data-line-number="12" data-line-start="12" data-line-end="12"><div class="line-content"><span class="mtk1">│   │       └── doctors.py   # 医生相关 API</span></div></div><div class="code-line" data-line-number="13" data-line-start="13" data-line-end="13"><div class="line-content"><span class="mtk1">│   └── requirements.txt</span></div></div><div class="code-line" data-line-number="14" data-line-start="14" data-line-end="14"><div class="line-content"><span class="mtk1">├── frontend/                 # Vue3 前端 (后续阶段)</span></div></div><div class="code-line" data-line-number="15" data-line-start="15" data-line-end="15"><div class="line-content"><span class="mtk1">└── DataProcess/              # 已有数据处理脚本</span></div></div></div></div></div></pre>

---

### Backend Dependencies

#### [NEW]

requirements.txt

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk1">fastapi>=0.100.0</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk1">uvicorn[standard]>=0.22.0</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk1">pandas>=2.0.0</span></div></div><div class="code-line" data-line-number="4" data-line-start="4" data-line-end="4"><div class="line-content"><span class="mtk1">scikit-learn>=1.3.0</span></div></div><div class="code-line" data-line-number="5" data-line-start="5" data-line-end="5"><div class="line-content"><span class="mtk1">SQLAlchemy>=2.0.0</span></div></div><div class="code-line" data-line-number="6" data-line-start="6" data-line-end="6"><div class="line-content"><span class="mtk1">python-multipart>=0.0.6</span></div></div></div></div></div></pre>

---

### Database Models

#### [NEW]

models.py

设计三个核心表：

**1. Doctor (医生表)** - 存储聚合后的医生画像

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk9 mtkb">class</span><span class="mtk1"></span><span class="mtk10">Doctor</span><span class="mtk1">:</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk1">    npi: </span><span class="mtk8">str</span><span class="mtk1"> (</span><span class="mtk10">PK</span><span class="mtk1">)           </span><span class="mtk3 mtki"># National Provider Identifier</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk1">    first_name: </span><span class="mtk8">str</span></div></div><div class="code-line" data-line-number="4" data-line-start="4" data-line-end="4"><div class="line-content"><span class="mtk1">    last_name: </span><span class="mtk8">str</span></div></div><div class="code-line" data-line-number="5" data-line-start="5" data-line-end="5"><div class="line-content"><span class="mtk1">    primary_type: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># 医生类型</span></div></div><div class="code-line" data-line-number="6" data-line-start="6" data-line-end="6"><div class="line-content"><span class="mtk1">    specialty: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># 专科</span></div></div><div class="code-line" data-line-number="7" data-line-start="7" data-line-end="7"><div class="line-content"><span class="mtk1">    state: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># 所在州</span></div></div><div class="code-line" data-line-number="8" data-line-start="8" data-line-end="8"><div class="line-content"><span class="mtk1">    cluster_id: </span><span class="mtk8">int</span><span class="mtk1"> (</span><span class="mtk10">FK</span><span class="mtk1">)    </span><span class="mtk3 mtki"># 所属聚类</span></div></div><div class="code-line" data-line-number="9" data-line-start="9" data-line-end="9"><div class="line-content"><span class="mtk1"></span><span class="mtk3 mtki"># RFM 计算值</span></div></div><div class="code-line" data-line-number="10" data-line-start="10" data-line-end="10"><div class="line-content"><span class="mtk1">    recency_days: </span><span class="mtk8">int</span><span class="mtk1"></span><span class="mtk3 mtki"># 最近交易距今天数</span></div></div><div class="code-line" data-line-number="11" data-line-start="11" data-line-end="11"><div class="line-content"><span class="mtk1">    frequency: </span><span class="mtk8">int</span><span class="mtk1"></span><span class="mtk3 mtki"># 交易次数</span></div></div><div class="code-line" data-line-number="12" data-line-start="12" data-line-end="12"><div class="line-content"><span class="mtk1">    monetary: </span><span class="mtk8">float</span><span class="mtk1"></span><span class="mtk3 mtki"># 总金额</span></div></div></div></div></div></pre>

**2. PaymentRecord (支付记录表)** - 存储清洗后的原始支付记录

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk9 mtkb">class</span><span class="mtk1"></span><span class="mtk10">PaymentRecord</span><span class="mtk1">:</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk1"></span><span class="mtk7">id</span><span class="mtk1">: </span><span class="mtk8">int</span><span class="mtk1"> (</span><span class="mtk10">PK</span><span class="mtk1">)</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk1">    npi: </span><span class="mtk8">str</span><span class="mtk1"> (</span><span class="mtk10">FK</span><span class="mtk1"></span><span class="mtk5">-></span><span class="mtk1"> Doctor)</span></div></div><div class="code-line" data-line-number="4" data-line-start="4" data-line-end="4"><div class="line-content"><span class="mtk1">    amount: </span><span class="mtk8">float</span></div></div><div class="code-line" data-line-number="5" data-line-start="5" data-line-end="5"><div class="line-content"><span class="mtk1">    payment_date: date</span></div></div><div class="code-line" data-line-number="6" data-line-start="6" data-line-end="6"><div class="line-content"><span class="mtk1">    payment_type: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># Nature_of_Payment</span></div></div><div class="code-line" data-line-number="7" data-line-start="7" data-line-end="7"><div class="line-content"><span class="mtk1">    manufacturer_name: </span><span class="mtk8">str</span></div></div><div class="code-line" data-line-number="8" data-line-start="8" data-line-end="8"><div class="line-content"><span class="mtk1">    product_name: </span><span class="mtk8">str</span></div></div></div></div></div></pre>

**3. ClusterResult (聚类结果表)** - 存储 K-Means 聚类结果

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk9 mtkb">class</span><span class="mtk1"></span><span class="mtk10">ClusterResult</span><span class="mtk1">:</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk1">    cluster_id: </span><span class="mtk8">int</span><span class="mtk1"> (</span><span class="mtk10">PK</span><span class="mtk1">)</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk1">    cluster_name: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># 如 "高价值核心客户"</span></div></div><div class="code-line" data-line-number="4" data-line-start="4" data-line-end="4"><div class="line-content"><span class="mtk1">    size_count: </span><span class="mtk8">int</span></div></div><div class="code-line" data-line-number="5" data-line-start="5" data-line-end="5"><div class="line-content"><span class="mtk1">    size_percentage: </span><span class="mtk8">float</span></div></div><div class="code-line" data-line-number="6" data-line-start="6" data-line-end="6"><div class="line-content"><span class="mtk1">    kpi_summary: </span><span class="mtk10">JSON</span><span class="mtk1"></span><span class="mtk3 mtki"># 平均 R/F/M, Top Specialty 等</span></div></div><div class="code-line" data-line-number="7" data-line-start="7" data-line-end="7"><div class="line-content"><span class="mtk1">    strategy_focus: </span><span class="mtk8">str</span><span class="mtk1"></span><span class="mtk3 mtki"># AI 生成的策略建议</span></div></div></div></div></div></pre>

---

#### [NEW]

database.py

配置 SQLite 数据库连接和 Session 管理。

---

#### [NEW]

config.py

使用 Pydantic Settings 管理配置 (数据库路径、API 密钥等)。

---

## Verification Plan

### Automated Tests

1. **数据库模型初始化测试** :

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk7">cd</span><span class="mtk1"></span><span class="mtk4">e:</span><span class="mtk10">\P</span><span class="mtk4">harmaAgentSystem</span><span class="mtk10">\b</span><span class="mtk4">ackend</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk7">python</span><span class="mtk1"></span><span class="mtk10">-c</span><span class="mtk1"></span><span class="mtk4">"from app.models import Base, engine; Base.metadata.create_all(engine); print('Database initialized successfully')"</span></div></div></div></div></div></pre>

1. **依赖安装验证** :

<pre><div node="[object Object]" class="relative whitespace-pre-wrap word-break-all p-3 my-2 rounded-sm bg-list-hover-subtle"><div><div class="code-block"><div class="code-line" data-line-number="1" data-line-start="1" data-line-end="1"><div class="line-content"><span class="mtk7">cd</span><span class="mtk1"></span><span class="mtk4">e:</span><span class="mtk10">\P</span><span class="mtk4">harmaAgentSystem</span><span class="mtk10">\b</span><span class="mtk4">ackend</span></div></div><div class="code-line" data-line-number="2" data-line-start="2" data-line-end="2"><div class="line-content"><span class="mtk7">pip</span><span class="mtk1"></span><span class="mtk4">install</span><span class="mtk1"></span><span class="mtk10">-r</span><span class="mtk1"></span><span class="mtk4">requirements.txt</span></div></div><div class="code-line" data-line-number="3" data-line-start="3" data-line-end="3"><div class="line-content"><span class="mtk7">pip</span><span class="mtk1"></span><span class="mtk4">list</span><span class="mtk1"></span><span class="mtk8">|</span><span class="mtk1"></span><span class="mtk7">findstr</span><span class="mtk1"></span><span class="mtk4">fastapi</span></div></div></div></div></div></pre>

### Manual Verification

1. 确认 `backend/pharma.db` 文件已创建
2. 使用 SQLite 工具 (如 DB Browser for SQLite) 查看表结构是否正确

---

## Data Processing Strategy (来自 analysis_assumptions.md)

| 数据问题            | 清洗策略                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------ |
| NPI 缺失 (0.31%)    | 删除缺失行                                                                                 |
| 日期格式            | 统一转换为 `YYYY-MM-DD`                                                                  |
| 金额为 0            | 保留 (可能为免费样品)                                                                      |
| Recipient Type 过滤 | 仅保留 `Covered Recipient Physician` 和 `Covered Recipient Non-Physician Practitioner` |
