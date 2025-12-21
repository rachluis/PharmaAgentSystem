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
