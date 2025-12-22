# Role: Senior Full-Stack Developer & UI/UX Expert

# Context

项目目前已完成基础功能开发（FastAPI 后端 + Vue3 前端），但在 **用户体验 (UX)、界面视觉比例 (UI Proportion)、交互细节** 以及 **业务逻辑完整性** 上仍有较大差距。

作为产品经理，我经过验收发现了以下核心问题，请务必仔细阅读并按模块逐一修复。

# 🚨 Critical Fixes & Improvements (P0)

## 1. 全局布局与比例优化 (Global Layout & Visual Hierarchy)

 **问题现状** : 页面在浏览器中显示比例失调，内容偏长，留白过大或过挤，没有自适应屏幕高度，导致视觉上“空旷”且“奇怪”。
 **优化指令** :

* **布局容器 (Container)** : 确保 `MainLayout.vue` 使用 `100vh` 布局。
* Header: 固定高度 (e.g., `60px`).
* Sidebar: 固定宽度 (展开 `240px`/收起 `64px`)，高度 `calc(100vh - 60px)`.
* Main Content: **必须** 设置 `overflow-y: auto` 和 `height: 100%`，防止整个页面滚动，只让内容区滚动。
* **内容密度** : 调整 `el-card` 和 `el-table` 的边距 (Padding/Margin)。不要让一个简单的表格撑满 3000px 高度。
* 使用 CSS Grid 或 Flex 布局，让 Dashboard 的图表在宽屏下横向排列（如 `el-col :span="12"` 或 `:span="8"`），而不是垂直堆叠。
* **响应式** : 确保所有页面在 `1366x768` 和 `1920x1080` 下都能舒适展示，不出现横向滚动条。

## 2. 身份认证模块重构 (Authentication 2.0)

 **问题现状** : 逻辑简陋，缺乏验证，UI 不够现代化。
 **优化指令 (Login.vue & Register.vue)** :

1. **UI 升级** :

* 字体: 使用更鲜明、现代的无衬线字体 (如 Inter, Roboto, PingFang SC)，加粗标题。
* 交互: 输入框增加 Focus 时的光晕效果；按钮增加 Hover 时的微抬起 (`transform: translateY(-2px)`) 和阴影加深效果。
* 布局: 保持左右分栏，但调整比例为 4:6 或 5:5，让表单在屏幕正中央，不要太宽。

1. **登录逻辑完善** :

* **错误处理** : 模拟后端返回“用户不存在”或“密码错误”，在前端显示红色 `el-alert` 或 `ElMessage.error`。不要只是 console.log。
* **防爆破** : 前端增加计数器，连续输错 5 次密码，禁用登录按钮 60秒（可使用 LocalStorage 暂存状态）。
* **记住我 (Remember Me)** : 勾选后，将加密后的用户名/密码（或 Token）存入 LocalStorage，下次打开页面自动填充。
* **找回密码 (Mock)** : 增加“忘记密码”链接，点击弹窗提示“请联系管理员重置”或跳转到一个模拟的“发送邮件”页面。

1. **注册逻辑升级** :

* **二次确认** : 增加 `confirm_password` 字段。使用 `validator` 确保两次输入一致，否则报错。
* **输入限制** :
  * 用户名: 长度 4-20 位，只允许字母数字。
  * 密码: 长度 8-20 位，必须包含字母和数字。
* **体验优化** : 注册成功后，自动跳转回登录页，并**自动填入**刚才注册的用户名，光标聚焦到密码框。

## 3. 侧边栏交互升级 (Sidebar UX)

 **问题现状** : 底部空缺，功能单一。
 **优化指令 (Sidebar.vue)** :

1. **底部功能区** :

* 使用 Flex 布局将 `el-menu` 撑开 (`flex: 1`)，在侧边栏最底部增加一个固定区域。
* 放置 **“设置 (Settings)”** 图标和 **“折叠/展开”** 按钮。
* 功能: 点击设置弹出抽屉 (Drawer)，支持修改 **主题色** (Primary Color) 和 **深色模式** 切换。

1. **折叠交互** :

* 实现侧边栏折叠逻辑（控制宽度 240px -> 64px）。
* **关键点** : 折叠后，菜单文字必须隐藏，只显示 Icon。鼠标悬浮在 Icon 上时，使用 `el-tooltip` 或 Element Plus 默认的 Popper 显示菜单名称。

## 4. 医生管理页面重构 (Doctor Management)

 **问题现状** : 姓名缺失，筛选难用，布局空旷。
 **优化指令 (DoctorListView.vue)** :

1. **数据显示修复** :

* 后端数据返回的是 `first_name` 和 `last_name`，前端 `el-table` 列需要使用 formatter 或 slot 拼接显示为 `Full Name`。
* 示例: `<template #default="scope">{{ scope.row.first_name }} {{ scope.row.last_name }}</template>`

1. **高级筛选区 (Filter Bar)** :

* **布局** : 将筛选条件放入一个 `el-collapse` 面板中，默认展开。
* **样式** : 调整输入框宽度，不要占满一行。一行放 3-4 个条件 (Grid 布局)。
* **自动填入 (Click-to-Filter)** : 这是一个这是亮点功能。
  * 为表格中的“专科 (Specialty)”和“州 (State)”列增加点击事件 `@click="applyFilter('state', row.state)"`。
  * 点击后，自动将该值填入顶部的筛选框，并触发搜索。

1. **视觉比例** :

* 设置表格高度为 `calc(100vh - 250px)`，固定表头，让表格内容内部滚动，而不是让整个页面滚动。
  列表信息字段增加颜色对比（不同专业之间，字体调整，），美观舒适

## 5. Dashboard 图表布局 (Dashboard Fix)

 **问题现状** : 图表颜色尚可，但排列比例奇怪（可能是一行一个大图，太高了）。
 **优化指令 (DashboardView.vue)** :

1. **栅格系统** :

* 第一行 (KPI): 4 个卡片，每个 `:span="6"`。
* 第二行 (主要趋势): 2 个图表，每个 `:span="12"` (左右各半)，高度固定为 `350px`。
* 第三行 (详细分析): 1 个宽图表 `:span="24"` 或 3 个小图表 `:span="8"`，高度固定 `300px`。

1. **ECharts 自适应** :

* 确保监听窗口 `resize` 事件，调用 `chart.resize()`，防止布局调整后图表变形。

# Execution Order (执行顺序)

请按照以下顺序执行修改，每完成一步请进行自测：

1. **Step 1** : 修复 `MainLayout.vue` 和 `Sidebar.vue` (布局容器 & 侧边栏升级)。
2. **Step 2** : 重写 `Login.vue` 和 `Register.vue` (认证体验)。
3. **Step 3** : 优化 `DashboardView.vue` (图表比例)。
4. **Step 4** : 重构 `DoctorListView.vue` (姓名显示、筛选交互)。

**请开始执行 Step 1。**
