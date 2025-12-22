# 系统日志与审计模块设计文档 (System Logs Design)

## 1. 模块概述

本模块旨在记录系统中的关键活动，包括用户登录行为和关键业务操作（如增删改数据）。日志数据将用于安全审计、用户行为分析及系统故障排查。

## 2. 功能需求 (Functional Requirements)

### 2.1 登录日志 (Login Logs)

* **记录触发** : 每次用户调用 `/api/auth/login` 时触发。
* **记录内容** :
* 用户名 (Username)
* 登录时间 (Time)
* 登录 IP 地址 (IP Address)
* 登录地点 (Location) - *可选，需调用 IP 库*
* 浏览器/设备信息 (User Agent)
* 状态 (Status): 成功/失败
* 失败原因 (Message): 如“密码错误”、“用户不存在”。

### 2.2 操作日志 (Operation Logs)

* **记录触发** : 拦截所有 **非 GET** 请求（POST, PUT, DELETE），或特定的关键 GET 请求。
* **记录内容** :
* 操作人 (Operator): 当前登录用户的 username。
* 模块 (Module): 如“医生管理”、“设置中心”。
* 动作 (Action): 如“新增医生”、“删除医生”。
* 请求路径 (URL) & 方法 (Method).
* 请求参数 (Params): 记录修改了什么数据（需脱敏）。
* 耗时 (Latency): 接口响应时间。
* 状态 (Status): 200 OK / 500 Error.

### 2.3 日志管理界面 (Frontend)

* **列表展示** : 分页展示日志，支持按时间倒序排列。
* **高级筛选** :
* 按操作人搜索。
* 按模块/类型筛选。
* 按日期范围筛选。
* 按状态（成功/失败）筛选。
* **详情查看** : 点击某条日志，弹窗显示详细的 JSON 请求/响应数据（方便排查 Bug）。
* **导出** : 支持导出日志为 Excel。

## 3. 数据库设计 (Database Schema)

需要新增表(需要的话)，目前数据库中有一张system_logs表。

### 3.1 `sys_login_logs`

| 字段           | 类型         | 说明           |
| -------------- | ------------ | -------------- |
| `id`         | Integer (PK) | 自增主键       |
| `username`   | String       | 登录账号       |
| `ip_address` | String       | IP 地址        |
| `browser`    | String       | 浏览器信息     |
| `os`         | String       | 操作系统       |
| `status`     | Integer      | 1=成功, 0=失败 |
| `message`    | String       | 提示信息       |
| `login_time` | DateTime     | 登录时间       |

### 3.2 `sys_op_logs`

| 字段            | 类型         | 说明                                  |
| --------------- | ------------ | ------------------------------------- |
| `id`          | Integer (PK) | 自增主键                              |
| `username`    | String       | 操作人账号                            |
| `module`      | String       | 所属模块 (如 "Doctor")                |
| `summary`     | String       | 操作简述 (如 "Create Doctor NPI 123") |
| `method`      | String       | HTTP 方法 (POST/PUT...)               |
| `path`        | String       | 请求路径                              |
| `params`      | Text/JSON    | 请求参数                              |
| `status`      | Integer      | 响应状态码 (200, 400, 500)            |
| `latency_ms`  | Integer      | 耗时 (毫秒)                           |
| `create_time` | DateTime     | 操作时间                              |
| `error_msg`   | Text         | 报错堆栈 (仅失败时记录)               |

## 4. 技术实现方案 (Middleware)

为了避免在每个接口中重复编写日志代码，将采用 **FastAPI Middleware (中间件)** + **BackgroundTasks** 方案。

1. **Middleware** : 拦截请求，记录开始时间。
2. **Process** : 等待接口处理完成。
3. **After Request** : 计算耗时，获取 Response 状态。
4. **Background Task** : 异步将日志写入数据库（不阻塞主线程）。
