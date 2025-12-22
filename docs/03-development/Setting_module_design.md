# 个人中心与系统设置模块设计文档 (User Settings Design Doc)

## 1. 模块概述

本模块旨在允许登录用户管理其个人账户信息、安全设置以及系统偏好。入口位于系统顶部导航栏（Header）右上角的个人头像/昵称处，通过下拉菜单进入。

## 2. 功能需求 (Functional Requirements)

### 2.1 个人信息管理 (Profile)

* **头像上传** : 支持用户上传/修改头像（若后端未实现文件服务，暂用 Mock 或 URL 链接）。
* **基础信息修改** :
* **昵称/真实姓名 (Full Name)** : 必填。
* **电子邮箱 (Email)** : 必填，需校验格式。
* **手机号 (Phone)** : 选填。
* **个人简介 (Bio)** : 选填。

### 2.2 安全设置 (Security)

* **修改密码** :
* 输入旧密码 (Old Password)。
* 输入新密码 (New Password)。
* 确认新密码 (Confirm Password)。
* *逻辑* : 后端需验证旧密码是否正确，新密码强度校验。

### 2.3 系统偏好 (Preferences) - *Optional*

* **主题色设置** : 选择系统主色调（蓝色、紫色、绿色等）。
* **侧边栏开关** : 开启/关闭侧边栏折叠。

## 3. UI/UX 设计方案

### 3.1 入口设计 (Header Dropdown)

* 在 Layout 的顶部导航栏右侧，显示 `Avatar` 和 `Username`。
* **交互** : 鼠标悬停或点击，弹出下拉菜单 (`el-dropdown`)。
* **菜单项** :

1. 个人中心 (User Profile) -> 跳转 `/settings?tab=profile`
2. 修改密码 (Change Password) -> 跳转 `/settings?tab=security`
3. 退出登录 (Logout) -> 调用 Logout 逻辑

### 3.2 设置页面布局 (`/views/settings/index.vue`)

* **布局** : 采用 **左右分栏** 或 **顶部 Tab** 结构。建议使用 `el-tabs` (Tab Position: left) 实现垂直导航。
* **Tab 1: 基础设置 (Basic Settings)**
  * 头部：头像展示与上传按钮。
  * 主体：`el-form` 表单，保存按钮。
* **Tab 2: 安全设置 (Security)**
  * 主体：修改密码表单。

## 4. API 接口定义 (Backend)

| 方法     | URL                        | 功能             | 参数 (Body)                                      |
| -------- | -------------------------- | ---------------- | ------------------------------------------------ |
| `GET`  | `/api/users/me`          | 获取当前用户信息 | -                                                |
| `PUT`  | `/api/users/me`          | 更新基础信息     | `{ full_name, email, phone, bio, avatar_url }` |
| `POST` | `/api/users/me/password` | 修改密码         | `{ old_password, new_password }`               |

## 5. 数据库变更 (`models.py`)

确保 `User` 表包含以下字段（如果没有需添加）：

* `email` (String)
* `full_name` (String)
* `phone` (String)
* `avatar` (String) - 存储图片 URL
* `bio` (Text)
