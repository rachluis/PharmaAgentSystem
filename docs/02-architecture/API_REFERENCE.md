# API 接口文档

> **PharmaAgent System - RESTful API Reference**
> Base URL: `http://127.0.0.1:8000/api/v1`

---

## 📋 目录

1. [通用说明](#1-通用说明)
2. [认证授权 (Auth)](#2-认证授权-auth)
3. [医生管理 (Doctors)](#3-医生管理-doctors)
4. [聚类分析 (Analysis)](#4-聚类分析-analysis)
5. [AI报告 (Reports)](#5-ai报告-reports)
6. [系统日志 (System)](#6-系统日志-system)
7. [用户管理 (Users)](#7-用户管理-users)
8. [错误码定义](#8-错误码定义)

---

## 1. 通用说明

### 1.1 请求格式

所有请求使用 **JSON** 格式：

```http
Content-Type: application/json
```

### 1.2 认证方式

除登录/注册接口外，所有接口需携带 **JWT Token**：

```http
Authorization: Bearer <your_access_token>
```

**获取Token**：调用 `POST /auth/login` 接口。

### 1.3 响应格式

#### 成功响应
```json
{
  "code": 200,
  "data": { ... },
  "message": "Success"
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "Error description",
  "detail": "Detailed error info"
}
```

### 1.4 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码（从1开始） |
| `page_size` | int | 20 | 每页条数（1-100） |

**分页响应格式**：
```json
{
  "total": 738772,
  "items": [ ... ]
}
```

---

## 2. 认证授权 (Auth)

### 2.1 用户注册

```http
POST /auth/register
```

**请求体**：
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone": "+1-555-1234",
  "bio": "Sales representative"
}
```

**响应**：
```json
{
  "code": 201,
  "message": "User registered successfully"
}
```

**字段说明**：
- `username`：必填，3-50字符，唯一
- `email`：必填，符合邮箱格式，唯一
- `password`：必填，6-72字符
- `full_name`、`phone`、`bio`：可选

---

### 2.2 用户登录

```http
POST /auth/login
```

**请求体**（使用 `application/x-www-form-urlencoded`）：
```
username=john_doe
password=SecurePass123
```

**响应**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "viewer",
    "avatar_url": "/uploads/avatars/1_xxx.jpg"
  }
}
```

**Token有效期**：24小时（86400秒）

---

### 2.3 获取当前用户信息

```http
GET /auth/me
```

**请求头**：
```http
Authorization: Bearer <token>
```

**响应**：
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "role": "analyst",
  "avatar_url": "/uploads/avatars/1_uuid.jpg",
  "is_active": true
}
```

---

### 2.4 更新用户资料

```http
PUT /auth/profile
```

**请求体**：
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "phone": "+1-555-5678",
  "bio": "Senior Analyst"
}
```

**响应**：返回更新后的用户对象。

---

### 2.5 修改密码

```http
POST /auth/change-password
```

**请求体**：
```json
{
  "old_password": "OldPass123",
  "new_password": "NewSecurePass456"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "Password changed successfully"
}
```

---

### 2.6 上传头像

```http
POST /auth/upload-avatar
```

**请求体**（multipart/form-data）：
```
file: <image file>
```

**限制**：
- 格式：JPG、PNG、GIF、WEBP
- 大小：最大5MB

**响应**：返回更新后的用户对象（包含新头像URL）。

---

## 3. 医生管理 (Doctors)

### 3.1 获取医生列表

```http
GET /doctors?page=1&page_size=20&specialty=Cardiology&state=CA
```

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码 |
| `page_size` | int | 否 | 每页条数 |
| `specialty` | string[] | 否 | 专业筛选（多选） |
| `state` | string[] | 否 | 州筛选（多选） |
| `cluster_id` | int | 否 | 聚类ID |
| `min_monetary` | float | 否 | 最小金额 |
| `max_monetary` | float | 否 | 最大金额 |
| `min_frequency` | int | 否 | 最小频次 |
| `max_frequency` | int | 否 | 最大频次 |
| `search` | string | 否 | 搜索（姓名/NPI） |

**响应**：
```json
{
  "total": 738772,
  "items": [
    {
      "npi": "1234567890",
      "first_name": "John",
      "last_name": "Smith",
      "specialty": "Cardiology",
      "state": "CA",
      "recency_days": 30,
      "frequency": 45,
      "monetary": 15000.50,
      "cluster_id": 0,
      "cluster_label": "High-Value"
    },
    ...
  ]
}
```

---

### 3.2 获取医生详情

```http
GET /doctors/{npi}
```

**路径参数**：
- `npi`：医生NPI编号（10位数字）

**响应**：
```json
{
  "doctor": {
    "npi": "1234567890",
    "first_name": "John",
    "last_name": "Smith",
    "full_name": "John Smith",
    "specialty": "Cardiology",
    "state": "CA",
    "city": "Los Angeles",
    "recency_days": 30,
    "frequency": 45,
    "monetary": 15000.50,
    "cluster_id": 0,
    "cluster_label": "High-Value"
  },
  "recent_payments": [
    {
      "id": 1001,
      "amount": 500.00,
      "payment_date": "2024-12-15",
      "payment_type": "Consulting Fee",
      "manufacturer_name": "Pfizer"
    },
    ...
  ]
}
```

---

### 3.3 创建医生

```http
POST /doctors
```

**请求体**：
```json
{
  "npi": "1234567890",
  "first_name": "Jane",
  "last_name": "Doe",
  "specialty": "Oncology",
  "state": "NY",
  "primary_type": "Medical Doctor"
}
```

**响应**：返回创建的医生对象（HTTP 201）。

---

### 3.4 更新医生

```http
PUT /doctors/{npi}
```

**请求体**（部分更新）：
```json
{
  "specialty": "Hematology-Oncology",
  "state": "CA"
}
```

**响应**：返回更新后的医生对象。

---

### 3.5 删除医生

```http
DELETE /doctors/{npi}
```

**响应**：HTTP 204 No Content

---

### 3.6 获取医生统计

```http
GET /doctors/statistics
```

**响应**：
```json
{
  "total_doctors": 738772,
  "total_monetary": 2495382940.50,
  "avg_monetary": 3377.92,
  "avg_frequency": 15.82,
  "specialty_distribution": {
    "Cardiology": 125000,
    "Internal Medicine": 98000,
    ...
  },
  "state_distribution": {
    "CA": 95000,
    "NY": 72000,
    ...
  }
}
```

**缓存策略**：结果缓存1小时，提升性能。

---

### 3.7 批量导入医生

```http
POST /doctors/batch/import
```

**请求体**（multipart/form-data）：
```
file: <CSV or Excel file>
```

**文件格式**：
- CSV/Excel文件
- 必填列：`npi`、`first_name`、`last_name`
- 可选列：`specialty`、`state`、`primary_type`

**响应**：
```json
{
  "status": "success",
  "message": "Successfully imported 500 doctors.",
  "total_records": 520,
  "inserted": 500,
  "skipped_duplicates": 20
}
```

---

## 4. 聚类分析 (Analysis)

### 4.1 创建聚类任务

```http
POST /analysis/tasks
```

**请求体**：
```json
{
  "task_name": "Q4 2024 Clustering",
  "task_type": "clustering",
  "parameters": {
    "k": 3,
    "features": ["recency_days", "frequency", "monetary"]
  }
}
```

**响应**：
```json
{
  "task_id": 101,
  "status": "pending",
  "created_at": "2024-12-25T10:30:00Z"
}
```

**任务状态**：
- `pending`：等待执行
- `running`：执行中
- `completed`：完成
- `failed`：失败

---

### 4.2 查询任务状态

```http
GET /analysis/tasks/{task_id}
```

**响应**：
```json
{
  "task_id": 101,
  "task_name": "Q4 2024 Clustering",
  "status": "completed",
  "progress": 100,
  "started_at": "2024-12-25T10:30:05Z",
  "completed_at": "2024-12-25T10:30:28Z",
  "result_id": 5
}
```

---

### 4.3 获取聚类结果

```http
GET /analysis/tasks/{task_id}/results
```

**响应**：
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "cluster_name": "High-Value",
      "size_count": 316000,
      "size_percentage": 42.8,
      "kpi_summary": {
        "avg_recency_days": 25.3,
        "avg_frequency": 48.2,
        "avg_monetary": 7713.50,
        "top_specialty": "Cardiology"
      },
      "silhouette_score": 0.65
    },
    {
      "cluster_id": 1,
      "cluster_name": "Low-Value",
      "size_count": 422772,
      "size_percentage": 57.2,
      "kpi_summary": {
        "avg_recency_days": 180.5,
        "avg_frequency": 2.3,
        "avg_monetary": 126.40,
        "top_specialty": "Family Medicine"
      }
    }
  ],
  "visualization_data": [
    {
      "npi": "1234567890",
      "recency_days": 30,
      "frequency": 45,
      "monetary": 15000,
      "cluster": 0
    },
    ...
  ]
}
```

**可视化数据说明**：
- 采样返回（最多10,000个点），用于绘制3D散点图
- 完整数据存储在数据库中

---

## 5. AI报告 (Reports)

### 5.1 生成AI策略（流式）

```http
POST /reports/generate-stream
```

**请求体**：
```json
{
  "cluster_id": 0,
  "user_prompt": "侧重合规性和学术会议"
}
```

**响应**：Server-Sent Events (SSE) 流式输出

```
data: {"type": "chunk", "content": "## 1. 群体洞察\n"}
data: {"type": "chunk", "content": "该群体为高价值核心..."}
data: {"type": "done", "report_id": 201}
```

**客户端示例（JavaScript）**：
```javascript
const eventSource = new EventSource('/api/v1/reports/generate-stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    console.log(data.content);
  } else if (data.type === 'done') {
    console.log('Report ID:', data.report_id);
    eventSource.close();
  }
};
```

---

### 5.2 获取报告列表

```http
GET /reports?page=1&page_size=20&report_type=cluster_analysis
```

**查询参数**：
- `report_type`：报告类型（`cluster_analysis` / `doctor_profile`）
- `status`：状态（`draft` / `published` / `archived`）

**响应**：
```json
{
  "total": 15,
  "items": [
    {
      "report_id": 201,
      "report_title": "Cluster 0 Strategy - Q4 2024",
      "report_type": "cluster_analysis",
      "created_at": "2024-12-25T11:00:00Z",
      "related_cluster_id": 0,
      "view_count": 25
    },
    ...
  ]
}
```

---

### 5.3 获取报告详情

```http
GET /reports/{report_id}
```

**响应**：
```json
{
  "report_id": 201,
  "report_title": "Cluster 0 Strategy - Q4 2024",
  "report_type": "cluster_analysis",
  "report_content": "## 1. 群体洞察\n该群体为高价值核心医生...",
  "report_summary": "高价值医生群体，建议学术引领策略",
  "related_cluster_id": 0,
  "generated_by": 5,
  "created_at": "2024-12-25T11:00:00Z",
  "generation_time": 18.5
}
```

**report_content格式**：Markdown文本。

---

### 5.4 删除报告

```http
DELETE /reports/{report_id}
```

**响应**：HTTP 204 No Content

---

## 6. 系统日志 (System)

### 6.1 获取登录日志

```http
GET /system/logs/login?page=1&size=20&username=john&status=1
```

**查询参数**：
- `username`：用户名（模糊搜索）
- `status`：状态（`1`=成功，`0`=失败）

**响应**：
```json
{
  "total": 1523,
  "items": [
    {
      "id": 1001,
      "username": "john_doe",
      "ip_address": "192.168.1.100",
      "browser": "Chrome 120.0",
      "os": "Windows 11",
      "status": 1,
      "message": "Success",
      "login_time": "2024-12-25T08:30:15Z"
    },
    ...
  ]
}
```

---

### 6.2 获取操作日志

```http
GET /system/logs/operation?page=1&size=20&module=Doctor&method=POST
```

**查询参数**：
- `module`：模块（`Auth` / `Doctor` / `Analysis` / `Report`）
- `username`：操作人（模糊搜索）
- `method`：HTTP方法（`POST` / `PUT` / `DELETE`）

**响应**：
```json
{
  "total": 3421,
  "items": [
    {
      "id": 5001,
      "username": "admin",
      "module": "Doctor",
      "summary": "POST /doctors",
      "method": "POST",
      "path": "/api/v1/doctors",
      "status": 201,
      "latency_ms": 85,
      "create_time": "2024-12-25T09:15:30Z"
    },
    ...
  ]
}
```

---

### 6.3 导出登录日志

```http
GET /system/logs/login/export?username=john&status=1
```

**响应**：CSV文件（`Content-Type: text/csv`）

**文件内容示例**：
```csv
ID,Username,IP Address,Browser,OS,Status,Message,Login Time
1001,john_doe,192.168.1.100,Chrome 120.0,Windows 11,Success,Success,2024-12-25 08:30:15
...
```

---

### 6.4 导出操作日志

```http
GET /system/logs/operation/export?module=Doctor
```

**响应**：CSV文件

---

## 7. 用户管理 (Users)

### 7.1 获取用户列表（管理员）

```http
GET /users?page=1&page_size=20&role=analyst&search=john
```

**权限要求**：Admin

**查询参数**：
- `role`：角色筛选（`admin` / `analyst` / `viewer`）
- `is_active`：激活状态（`true` / `false`）
- `search`：搜索（用户名/邮箱/姓名）

**响应**：
```json
{
  "total": 45,
  "items": [
    {
      "id": 5,
      "username": "john_doe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "analyst",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z",
      "last_login": "2024-12-25T08:30:15Z"
    },
    ...
  ]
}
```

---

### 7.2 创建用户（管理员）

```http
POST /users
```

**权限要求**：Admin

**请求体**：
```json
{
  "username": "new_user",
  "email": "new@example.com",
  "password": "TempPass123",
  "full_name": "New User",
  "role": "viewer"
}
```

**响应**：返回创建的用户对象（HTTP 201）。

---

### 7.3 更新用户（管理员）

```http
PUT /users/{user_id}
```

**权限要求**：Admin

**请求体**：
```json
{
  "full_name": "Updated Name",
  "role": "analyst",
  "is_active": false
}
```

**响应**：返回更新后的用户对象。

---

### 7.4 删除用户（管理员）

```http
DELETE /users/{user_id}
```

**权限要求**：Admin

**限制**：无法删除自己。

**响应**：HTTP 204 No Content

---

### 7.5 重置用户密码（管理员）

```http
POST /users/{user_id}/reset-password
```

**权限要求**：Admin

**请求体**：
```json
{
  "new_password": "NewSecurePass456"
}
```

**响应**：
```json
{
  "message": "Password reset successfully"
}
```

---

### 7.6 获取用户统计（管理员）

```http
GET /users/statistics
```

**权限要求**：Admin

**响应**：
```json
{
  "total_users": 45,
  "active_users": 42,
  "inactive_users": 3,
  "role_distribution": {
    "admin": 2,
    "analyst": 15,
    "viewer": 28
  }
}
```

---

## 8. 错误码定义

| HTTP状态码 | Code | 说明 | 示例 |
|-----------|------|------|------|
| **200** | 200 | 成功 | 请求成功处理 |
| **201** | 201 | 已创建 | 成功创建资源 |
| **204** | 204 | 无内容 | 删除成功 |
| **400** | 400 | 请求错误 | 参数验证失败 |
| **401** | 401 | 未授权 | Token无效或过期 |
| **403** | 403 | 禁止访问 | 权限不足 |
| **404** | 404 | 未找到 | 资源不存在 |
| **422** | 422 | 验证失败 | Pydantic验证错误 |
| **500** | 500 | 服务器错误 | 数据库连接失败 |

### 常见错误示例

#### 401 未授权
```json
{
  "detail": "Could not validate credentials",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```

#### 403 权限不足
```json
{
  "code": 403,
  "detail": "Admin privileges required"
}
```

#### 422 验证失败
```json
{
  "code": 422,
  "message": "Validation error",
  "errors": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 📞 技术支持

- 🌐 在线API测试：http://localhost:8000/docs（Swagger UI）
- 📧 技术支持：api-support@pharmaagent.com
- 📖 完整文档：https://docs.pharmaagent.com

---

**最后更新**：2026-01-26
**API版本**：v1.0.0
**文档版本**：1.0.0
