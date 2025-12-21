# PharmaAgent System - Frontend

基于 Vue 3 + Vite 的医药市场分析系统前端界面。

## 🛠️ 技术栈

- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **UI Component**: Element Plus
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios

## 🚀 快速开始

### 1. 环境准备

确保已安装 Node.js (推荐 16+)。

```powershell
cd frontend
```

### 2. 安装依赖

```powershell
npm install
```

### 3. 配置开发环境

项目默认配置代理如下 (`vite.config.ts`)：

- `/api` -> `http://127.0.0.1:8000`
- `/uploads` -> `http://127.0.0.1:8000`

### 4. 启动开发服务器

```powershell
npm run dev
```

启动后访问: <http://localhost:5173>

## 📂 目录结构

- `src/`
  - `api/`: 后端 API 封装
  - `views/`: 页面视图 (Login, DoctorList, Analysis, Settings, SystemLogs)
  - `layout/`: 全局布局 (Sidebar, Header)
  - `stores/`: Pinia 状态管理 (User Store)
  - `router/`: 路由定义
