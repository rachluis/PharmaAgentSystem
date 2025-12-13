
# Role: Senior Frontend Developer (Vue 3 Expert)

# Context

* **项目状态** : 后端 (FastAPI) 已就绪，核心聚类 API 已完成测试。
* **当前目标** : 初始化前端项目，并搭建基础架构。
* **参考文件** : 请阅读 `Project_Progress_and_Roadmap.md` 了解整体架构。

# Task 5: 前端项目初始化与基础架构搭建

请在项目根目录下执行以下操作（请提供具体的 Terminal 命令和代码）：

## 1. 初始化项目 (Vite + Vue 3 + TS)

* 在根目录创建 `frontend` 文件夹。
* 使用 Vite 模板：`npm create vite@latest frontend -- --template vue-ts`
* 安装核心依赖：
  * `element-plus` (UI 组件库)
  * `@element-plus/icons-vue` (图标)
  * `axios` (网络请求)
  * `pinia` (状态管理)
  * `vue-router` (路由)
  * `echarts` (图表库)
  * `sass` (预处理器)

## 2. 项目配置

请生成/修改以下配置文件：

* **`vite.config.ts`** : 配置 server proxy，将 `/api` 的请求转发到 `http://127.0.0.1:8000` (后端地址)，解决跨域问题。
* **`src/main.ts`** : 引入 Element Plus 样式和 Pinia。

## 3. 核心模块封装

请在 `src` 目录下创建规范的目录结构，并编写以下基础代码：

* **`src/api/request.ts`** : 封装 Axios 实例。
* 设置 `baseURL: '/api'`。
* 添加响应拦截器：统一处理错误（如 400/500 弹出 Element Plus Message 错误提示）。
* **`src/api/analysis.ts`** : 定义调用后端聚类接口的函数。
* `performClustering(k: number)`
* `getAnalysisResults()`

## 4. 路由与布局 (Layout)

* **`src/router/index.ts`** : 定义基础路由 (`/`, `/analysis`, `/strategy`)。
* **`src/layout/MainLayout.vue`** :
* 使用 Element Plus 的 `<el-container>` 布局。
* 左侧：侧边栏菜单 (Sidebar)，包含“仪表盘”、“画像分析”、“策略生成”三个菜单项。
* 右侧：内容区域 (RouterView)。

## 前端功能规划 (Frontend Features)

### 用户认证模块 (Authentication)

* **登录页** : 简洁大气的 B 端登录界面，支持用户名/密码登录。
* **注册页** : 用户注册功能（暂存本地或简单数据库验证）。
* **权限控制** : 登录后获取 Token (或 Mock Token)，用于后续 API 请求鉴权。

### 基础业务模块 (Doctor Management)

* **医生列表页** :
* **表格展示** : 分页展示医生基本信息 (NPI, Name, Specialty, State)。
* **搜索/筛选** : 按姓名、科室、州进行搜索。
* **CRUD 操作** :
  * **查看详情** : 跳转到医生画像详情页。
  * **编辑** : 修改医生基本信息（模拟）。
  * **删除** : 软删除医生记录（模拟）。
* **数据导出** : 导出当前表格为 Excel/CSV。

### 核心分析模块 (Analysis Dashboard)

* **聚类概览** : 渲染雷达图、饼图、散点图。
* **策略报告** : 展示 AI 生成的 Markdown 报告。

## 接口需求 (Backend Requirements for Frontend)

前端开发需要后端提供（或由前端 Mock）以下接口支持：

* `POST /api/auth/login`: 登录接口。
* `POST /api/auth/register`: 注册接口。
* `GET /api/doctors`: 分页获取医生列表（支持 `search`, `page`, `size`）。
* `PUT /api/doctors/{npi}`: 更新医生信息。
* `DELETE /api/doctors/{npi}`: 删除医生。

**Execution Plan** :

1. 请先给出  **Terminal 安装命令** 。
2. 然后依次生成 `vite.config.ts`, `src/api/request.ts`, `src/router/index.ts`, 和 `src/layout/MainLayout.vue` 的代码。
