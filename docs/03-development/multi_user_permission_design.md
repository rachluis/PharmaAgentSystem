# 多用户权限管理与数据访问控制设计文档

**版本**: 1.0  
**最后更新**: 2025-01-XX  
**状态**: 设计阶段

---

## 📋 目录

1. [需求分析](#1-需求分析)
2. [权限模型设计](#2-权限模型设计)
3. [数据访问控制方案](#3-数据访问控制方案)
4. [数据库设计](#4-数据库设计)
5. [API 设计](#5-api-设计)
6. [前端实现](#6-前端实现)
7. [实施计划](#7-实施计划)

---

## 1. 需求分析

### 1.1 业务场景

当前系统是**单租户**模式，所有用户共享同一份数据（738K医生数据）。需要支持：

1. **多租户/多组织**：不同药企/组织拥有独立的数据集
2. **用户角色细分**：在现有 admin/analyst/viewer 基础上，增加组织内角色
3. **数据隔离**：用户只能访问所属组织的数据
4. **数据集管理**：支持数据导入、分配、共享

### 1.2 用户角色定义

#### 系统级角色（全局）
- **super_admin**: 超级管理员，可管理所有组织和用户
- **admin**: 组织管理员，管理本组织内的用户和数据

#### 组织级角色（组织内）
- **analyst**: 数据分析师，可执行分析任务、生成报告
- **viewer**: 查看者，只能查看数据和分析结果
- **data_manager**: 数据管理员，可导入、管理数据集

---

## 2. 权限模型设计

### 2.1 RBAC (基于角色的访问控制)

```
┌─────────────────────────────────────────┐
│          Permission (权限)              │
│  - doctors:read                         │
│  - doctors:write                        │
│  - analysis:execute                     │
│  - reports:generate                     │
│  - data:import                          │
└─────────────────────────────────────────┘
                    ↑
                    │ assigned to
                    │
┌─────────────────────────────────────────┐
│          Role (角色)                    │
│  - admin: [all permissions]            │
│  - analyst: [read, execute, generate]   │
│  - viewer: [read]                       │
│  - data_manager: [read, import]        │
└─────────────────────────────────────────┘
                    ↑
                    │ assigned to
                    │
┌─────────────────────────────────────────┐
│          User (用户)                    │
│  - user_id                              │
│  - organization_id                      │
│  - role                                 │
└─────────────────────────────────────────┘
```

### 2.2 权限矩阵

| 功能模块 | super_admin | admin | analyst | viewer | data_manager |
|---------|------------|-------|---------|--------|--------------|
| **用户管理** | ✅ 全部 | ✅ 本组织 | ❌ | ❌ | ❌ |
| **数据查看** | ✅ 全部 | ✅ 本组织 | ✅ 本组织 | ✅ 本组织 | ✅ 本组织 |
| **数据导入** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **数据分析** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **报告生成** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **系统设置** | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 3. 数据访问控制方案

### 3.1 数据隔离策略

#### 方案一：组织级数据隔离（推荐）

**核心思想**：每个组织拥有独立的数据集，通过 `organization_id` 关联

```python
# 数据表增加 organization_id
class Doctor(Base):
    npi = Column(String(10), primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    # ... 其他字段

# 查询时自动过滤
def get_doctors(db: Session, current_user: User, ...):
    query = db.query(Doctor)
    
    # 自动添加组织过滤
    if current_user.role != "super_admin":
        query = query.filter(Doctor.organization_id == current_user.organization_id)
    
    return query.all()
```

**优点**：
- 数据完全隔离，安全性高
- 查询性能好（有索引）
- 易于扩展

**缺点**：
- 需要数据迁移（为现有数据分配组织）
- 数据无法跨组织共享

#### 方案二：数据集标签（灵活但复杂）

**核心思想**：通过数据集（Dataset）概念，用户可访问多个数据集

```python
# 数据集表
class Dataset(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    is_public = Column(Boolean, default=False)  # 是否公开

# 用户-数据集关联表
class UserDataset(Base):
    user_id = Column(Integer, ForeignKey("users.id"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    access_level = Column(String(20))  # read, write, admin

# 医生-数据集关联表
class DoctorDataset(Base):
    doctor_id = Column(String(10), ForeignKey("doctors.npi"))
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
```

**优点**：
- 灵活，支持数据共享
- 支持多数据集访问

**缺点**：
- 查询复杂（需要 JOIN）
- 性能开销较大

### 3.2 推荐方案：混合模式

**第一阶段**：实现组织级隔离（方案一）
- 快速实现，满足基本需求
- 数据安全有保障

**第二阶段**：增加数据集共享功能（方案二）
- 支持组织间数据共享
- 支持公开数据集

---

## 4. 数据库设计

### 4.1 新增表结构

#### 4.1.1 organizations (组织表)

```sql
CREATE TABLE organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,  -- 组织代码，如 "PHARMA_A"
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE INDEX idx_organizations_code ON organizations(code);
```

#### 4.1.2 修改 users 表

```sql
ALTER TABLE users ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT 0;

CREATE INDEX idx_users_organization ON users(organization_id);
```

#### 4.1.3 修改 doctors 表

```sql
ALTER TABLE doctors ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
CREATE INDEX idx_doctors_organization ON doctors(organization_id);
```

#### 4.1.4 修改其他核心表

```sql
-- payment_records
ALTER TABLE payment_records ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
CREATE INDEX idx_payment_records_organization ON payment_records(organization_id);

-- cluster_results
ALTER TABLE cluster_results ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
CREATE INDEX idx_cluster_results_organization ON cluster_results(organization_id);

-- analysis_tasks
ALTER TABLE analysis_tasks ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
CREATE INDEX idx_analysis_tasks_organization ON analysis_tasks(organization_id);

-- ai_reports
ALTER TABLE ai_reports ADD COLUMN organization_id INTEGER REFERENCES organizations(id);
CREATE INDEX idx_ai_reports_organization ON ai_reports(organization_id);
```

#### 4.1.5 datasets 表（可选，第二阶段）

```sql
CREATE TABLE datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    organization_id INTEGER REFERENCES organizations(id),
    is_public BOOLEAN DEFAULT 0,
    created_by INTEGER REFERENCES users(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_datasets (
    user_id INTEGER REFERENCES users(id),
    dataset_id INTEGER REFERENCES datasets(id),
    access_level VARCHAR(20) DEFAULT 'read',  -- read, write, admin
    PRIMARY KEY (user_id, dataset_id)
);

CREATE TABLE doctor_datasets (
    doctor_id VARCHAR(10) REFERENCES doctors(npi),
    dataset_id INTEGER REFERENCES datasets(id),
    PRIMARY KEY (doctor_id, dataset_id)
);
```

### 4.2 数据迁移策略

```python
# 迁移脚本：为现有数据分配默认组织
def migrate_existing_data():
    # 1. 创建默认组织
    default_org = Organization(
        name="默认组织",
        code="DEFAULT",
        description="系统默认组织"
    )
    db.add(default_org)
    db.commit()
    
    # 2. 为所有现有用户分配组织
    db.query(User).update({User.organization_id: default_org.id})
    
    # 3. 为所有现有数据分配组织
    db.query(Doctor).update({Doctor.organization_id: default_org.id})
    db.query(PaymentRecord).update({PaymentRecord.organization_id: default_org.id})
    # ... 其他表
    
    db.commit()
```

---

## 5. API 设计

### 5.1 组织管理 API

```python
# POST /api/v1/organizations
# 创建组织（仅 super_admin）
@router.post("", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    ...

# GET /api/v1/organizations
# 获取组织列表
@router.get("", response_model=List[OrganizationResponse])
async def get_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # super_admin 看到所有，其他用户只看到自己的组织
    ...

# GET /api/v1/organizations/{id}
# 获取组织详情
@router.get("/{id}", response_model=OrganizationResponse)
async def get_organization(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查权限：只能查看自己组织的
    ...
```

### 5.2 数据访问控制中间件

```python
# backend/app/core/data_access.py
from sqlalchemy.orm import Query
from typing import TypeVar, Type
from sqlalchemy import Column

T = TypeVar('T')

def apply_organization_filter(
    query: Query[T],
    model: Type[T],
    current_user: User
) -> Query[T]:
    """
    自动为查询添加组织过滤
    """
    # super_admin 可以访问所有数据
    if current_user.is_super_admin:
        return query
    
    # 检查模型是否有 organization_id 字段
    if hasattr(model, 'organization_id'):
        query = query.filter(model.organization_id == current_user.organization_id)
    
    return query

# 使用示例
@router.get("/doctors")
async def get_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Doctor)
    query = apply_organization_filter(query, Doctor, current_user)
    return query.all()
```

### 5.3 权限装饰器增强

```python
# backend/app/core/security.py
def require_permission(permission: str):
    """
    基于权限的访问控制
    """
    async def permission_checker(current_user: User = Depends(get_current_user)):
        # 检查用户是否有该权限
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=403,
                detail=f"缺少权限: {permission}"
            )
        return current_user
    return permission_checker

# 权限定义
PERMISSIONS = {
    "admin": ["*"],  # 所有权限
    "analyst": ["doctors:read", "analysis:execute", "reports:generate"],
    "viewer": ["doctors:read"],
    "data_manager": ["doctors:read", "data:import"]
}

def has_permission(user: User, permission: str) -> bool:
    if user.is_super_admin:
        return True
    
    user_perms = PERMISSIONS.get(user.role, [])
    return "*" in user_perms or permission in user_perms
```

---

## 6. 前端实现

### 6.1 用户组织信息显示

```vue
<!-- MainLayout.vue -->
<template>
  <el-dropdown>
    <span class="user-info">
      <el-avatar :src="userStore.user?.avatar_url" />
      <span>{{ userStore.userName }}</span>
      <el-tag size="small" type="info">
        {{ userStore.organizationName }}
      </el-tag>
    </span>
  </el-dropdown>
</template>
```

### 6.2 权限控制组件

```vue
<!-- PermissionGuard.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  permission: string
  fallback?: boolean
}>()

const userStore = useUserStore()
const hasPermission = computed(() => {
  return userStore.hasPermission(props.permission)
})
</script>

<template>
  <slot v-if="hasPermission" />
  <slot v-else name="fallback" />
</template>
```

### 6.3 使用示例

```vue
<template>
  <!-- 只有分析师和管理员可以看到分析按钮 -->
  <PermissionGuard permission="analysis:execute">
    <el-button @click="startAnalysis">开始分析</el-button>
    <template #fallback>
      <el-button disabled>无权限</el-button>
    </template>
  </PermissionGuard>
</template>
```

---

## 7. 实施计划

### 阶段一：基础权限系统（1-2周）

1. **数据库迁移**
   - 创建 `organizations` 表
   - 为现有表添加 `organization_id`
   - 数据迁移脚本

2. **后端实现**
   - 组织管理 API
   - 数据访问控制中间件
   - 权限检查装饰器

3. **前端实现**
   - 组织选择/显示
   - 权限控制组件
   - 路由守卫增强

### 阶段二：用户管理增强（1周）

1. **组织内用户管理**
   - 用户列表（仅本组织）
   - 角色分配
   - 用户激活/禁用

2. **注册流程优化**
   - 支持组织邀请码注册
   - 管理员审核机制

### 阶段三：数据隔离验证（1周）

1. **测试数据隔离**
   - 创建多个测试组织
   - 验证数据完全隔离
   - 性能测试

2. **安全审计**
   - SQL 注入测试
   - 权限绕过测试

### 阶段四：数据集共享（可选，2-3周）

1. **数据集管理**
   - 数据集创建/删除
   - 数据分配

2. **共享机制**
   - 公开数据集
   - 跨组织共享

---

## 8. 安全考虑

### 8.1 SQL 注入防护

- 使用 SQLAlchemy ORM，避免原生 SQL
- 参数化查询

### 8.2 权限绕过防护

- 所有数据查询必须经过 `apply_organization_filter`
- 前端权限控制仅用于 UI 展示，后端必须验证

### 8.3 数据泄露防护

- 敏感数据脱敏（如医生姓名可配置）
- 操作日志记录所有数据访问

---

## 9. 总结

本设计实现了：

✅ **多租户支持**：组织级数据隔离  
✅ **细粒度权限**：基于角色的访问控制  
✅ **数据安全**：自动过滤，防止越权访问  
✅ **可扩展性**：支持未来数据集共享功能  

**下一步**：开始实施阶段一，创建数据库迁移脚本。

