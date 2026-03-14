# PharmaAgent System

PharmaAgent System 是一个集成了医药市场数据分析、医生画像构建、AI 策略生成及系统管理功能的综合平台。

## 🌟 系统模块

系统主要由以下两个部分组成：

1. **Backend (后端)**:
    - 基于 FastAPI 构建，提供 RESTful API。
    - 负责数据处理、K-Means 聚类分析、用户认证及日志管理。
    - [查看详细文档](./backend/README.md)

2. **Frontend (前端)**:
    - 基于 Vue 3 + Element Plus 构建。
    - 提供医生列表、数据大屏、分析任务管理及系统设置界面。
    - [查看详细文档](./frontend/README.md)

## 🚦 快速启动指南

### 1. 启动后端

```powershell
# 打开新终端
cd backend
# 激活虚拟环境 (可选)
# .\.venv\Scripts\Activate.ps1
# 启动服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 启动前端

```powershell
# 打开新终端
cd frontend
# 启动服务
npm run dev
```

### 3. 访问系统

打开浏览器访问: `http://localhost:5173`

默认测试账号 (如果已初始化):

- 用户名: `Rui_3`
- 密码: `password123`

## ✨ 核心功能

- **医生画像**: 聚合 CMS Open Payments 数据，计算 RFM 指标。
- **市场分析**: K-Means 聚类分析，识别核心客户群体。
- **系统日志**: 全面的登录与操作日志监控 (`/system/logs`)。
- **个人中心**: 支持头像上传及个人信息管理。

## 📚 文档中心

为保持根目录清爽，所有详细方案、实测数据报告以及毕业论文全稿均已归档至 [docs 目录](./docs/README.md)：

### 系统开发文档

- [快速开始](./docs/01-getting-started/quick_start.md)
- [系统架构分析](./docs/02-architecture/system_architecture_and_workflow.md)
- [开发实战指南](./docs/03-development/developer_guide_analysis.md)
- [数据字典与结构](./docs/04-data/DATA_DICTIONARY.md)

### 学术与实研补充文档 (🌟 New)

- **实测数据提取:** [docs/08-ai-extractions](./docs/08-ai-extractions/) (含聚类最优K值、数据库SQL探针耗时、AI报告原件等证明材料)
- **学术原稿与大纲:** [docs/09-academic](./docs/09-academic/) (含最新的第五、六章修订版，以及论文初稿与提示词)

---

> **Note:** 系统中临时测试脚本均已收纳至 `backend/scripts/archive`，以保持核心微服务的纯洁性。