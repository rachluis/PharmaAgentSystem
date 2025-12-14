# 🔧 后端开发完善指令 - Phase 1 详细任务

> **目标**：完善FastAPI后端，建立完整的数据库结构，实现所有核心API
> **当前状态**：项目骨架存在，pharma.db有数据，但模型和API不完整

---

## 🗄️ Task 1: 扩展数据库模型

### 命令给AI Agent：

```
请完善 backend/app/models.py，实现以下7张表的完整定义：

要求：
1. 保留现有的 Doctor 表结构，添加以下新字段：
   - full_name (VARCHAR(200))
   - city (VARCHAR(100))
   - cluster_label (VARCHAR(50))
   - total_payments (INTEGER, default=0)
   - avg_payment_amount (FLOAT, default=0.0)
   - last_payment_date (DATE)

2. 创建 User 表（用户认证）：
   - id: INTEGER, primary_key, autoincrement
   - username: VARCHAR(50), unique, not null
   - email: VARCHAR(100), unique, not null
   - password_hash: VARCHAR(255), not null
   - full_name: VARCHAR(100)
   - role: VARCHAR(20), default='viewer'  # admin/analyst/viewer
   - avatar_url: VARCHAR(255)
   - is_active: BOOLEAN, default=True
   - created_at: DATETIME, server_default=now()
   - updated_at: DATETIME, onupdate=now()
   - last_login: DATETIME

3. 创建 PaymentRecord 表（支付记录）：
   - id: INTEGER, primary_key
   - npi: VARCHAR(20), ForeignKey('doctors.npi')
   - payment_date: DATE, not null
   - amount: FLOAT, not null
   - payment_type: VARCHAR(100)
   - nature_of_payment: VARCHAR(200)
   - payer_name: VARCHAR(200)
   - created_at: DATETIME

4. 创建 AnalysisTask 表（分析任务）：
   - task_id: INTEGER, primary_key
   - task_name: VARCHAR(200), not null
   - task_type: VARCHAR(50)  # 'clustering', 'rfm_analysis'
   - parameters: TEXT  # JSON格式
   - status: VARCHAR(20), default='pending'  # pending/running/completed/failed
   - progress: INTEGER, default=0
   - created_by: INTEGER, ForeignKey('users.id')
   - started_at: DATETIME
   - completed_at: DATETIME
   - error_message: TEXT
   - result_id: INTEGER, ForeignKey('cluster_results.cluster_id')
   - created_at: DATETIME

5. 扩展现有的 ClusterResult 表，添加：
   - task_id: INTEGER, ForeignKey('analysis_tasks.task_id')
   - algorithm: VARCHAR(50), default='k-means'
   - features_used: TEXT  # JSON
   - cluster_labels: TEXT  # JSON: {"0": "核心客户", ...}
   - silhouette_score: FLOAT
   - inertia: FLOAT
   - visualization_data: TEXT  # JSON
   - is_active: BOOLEAN, default=True

6. 创建 AIReport 表（AI报告）：
   - report_id: INTEGER, primary_key
   - report_title: VARCHAR(300), not null
   - report_type: VARCHAR(50)  # 'cluster_analysis', 'doctor_profile'
   - report_content: TEXT, not null
   - report_summary: TEXT
   - related_cluster_id: INTEGER, ForeignKey('cluster_results.cluster_id')
   - related_npi: VARCHAR(20)
   - generated_by: INTEGER, ForeignKey('users.id')
   - dify_conversation_id: VARCHAR(100)
   - generation_time: FLOAT
   - status: VARCHAR(20), default='draft'
   - view_count: INTEGER, default=0
   - created_at: DATETIME
   - updated_at: DATETIME

7. 创建 SystemLog 表（系统日志）：
   - log_id: INTEGER, primary_key
   - user_id: INTEGER, ForeignKey('users.id')
   - action: VARCHAR(100)
   - module: VARCHAR(50)
   - ip_address: VARCHAR(50)
   - request_data: TEXT
   - response_status: INTEGER
   - created_at: DATETIME

重要：
- 所有外键要正确定义关系
- 为常用查询字段添加索引（username, email, npi, cluster_id等）
- 使用 server_default=func.now() 而不是 default=datetime.now()
- 确保与现有数据兼容（Doctor表已有数据）
```

**验证方法**：

```bash
# 运行后检查模型是否正确
python -c "from app.models import User, Doctor, AIReport; print('Models loaded successfully')"
```

---

## 🔐 Task 2: 实现安全模块 

### 命令给AI Agent：

```
请创建 backend/app/core/security.py，实现完整的JWT认证系统：

要求：

1. 导入必要的库：
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

2. 配置常量：
SECRET_KEY = "your-secret-key-change-in-production-09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

3. 实现以下函数：

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)

# JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """从Token获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
  
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
  
    from app.models import User
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
  
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取激活的用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

4. 添加角色检查函数：
def require_role(required_role: str):
    """角色权限装饰器"""
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != 'admin':
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker
```

**验证方法**：

```python
# 测试密码加密
from app.core.security import get_password_hash, verify_password
hashed = get_password_hash("test123")
print(verify_password("test123", hashed))  # 应该输出 True
```

---

## 📝 Task 3: 创建Pydantic Schemas (20分钟)

### 命令给AI Agent：

```
请完善 backend/app/schemas.py，创建所有API的请求/响应模型：

要求：

1. 用户相关Schemas：
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
  
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

2. 医生相关Schemas：
class DoctorBase(BaseModel):
    npi: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    specialty: Optional[str]
    state: Optional[str]
    city: Optional[str]

class DoctorResponse(DoctorBase):
    rfm_frequency: Optional[int]
    rfm_monetary: Optional[float]
    rfm_recency: Optional[datetime]
    cluster_id: Optional[int]
    cluster_label: Optional[str]
    total_payments: int
    avg_payment_amount: float
    last_payment_date: Optional[datetime]
  
    class Config:
        from_attributes = True

class DoctorListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[DoctorResponse]

class DoctorStatistics(BaseModel):
    total_doctors: int
    total_monetary: float
    avg_monetary: float
    avg_frequency: float
    specialty_distribution: dict
    state_distribution: dict
    cluster_distribution: dict

3. 分析相关Schemas：
class ClusteringRequest(BaseModel):
    k: int
    features: Optional[list[str]] = ["rfm_frequency", "rfm_monetary"]
    task_name: str

class ClusterResultResponse(BaseModel):
    cluster_id: int
    k_value: int
    cluster_stats: dict
    silhouette_score: Optional[float]
    cluster_labels: Optional[dict]
    created_at: datetime
  
    class Config:
        from_attributes = True

class AnalysisTaskResponse(BaseModel):
    task_id: int
    task_name: str
    status: str
    progress: int
    created_at: datetime
  
    class Config:
        from_attributes = True

4. 报告相关Schemas：
class ReportGenerateRequest(BaseModel):
    report_type: str  # 'cluster_analysis', 'doctor_profile'
    cluster_id: Optional[int]
    custom_prompt: Optional[str]
    title: Optional[str]

class ReportResponse(BaseModel):
    report_id: int
    report_title: str
    report_type: str
    report_summary: Optional[str]
    status: str
    view_count: int
    created_at: datetime
  
    class Config:
        from_attributes = True

class ReportDetailResponse(ReportResponse):
    report_content: str
    related_cluster_id: Optional[int]
    generation_time: Optional[float]

5. 通用响应Schema：
class APIResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
    timestamp: datetime = datetime.utcnow()
```

---

## 🛣️ Task 4: 实现认证API (30分钟)

### 命令给AI Agent：

```
请创建 backend/app/routers/auth.py，实现完整的认证功能：

要求：

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import User, SystemLog
from app.schemas import UserCreate, UserResponse, Token, PasswordChange
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    get_current_active_user
)

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 1. 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(400, "Username already exists")
  
    # 2. 检查邮箱是否存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email already exists")
  
    # 3. 创建用户
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role='viewer'  # 新用户默认为viewer
    )
  
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
  
    # 4. 记录日志
    log = SystemLog(
        user_id=db_user.id,
        action="register",
        module="auth"
    )
    db.add(log)
    db.commit()
  
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    # 1. 验证用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
  
    if not user.is_active:
        raise HTTPException(400, "User is inactive")
  
    # 2. 生成Token
    access_token = create_access_token(data={"sub": user.username})
  
    # 3. 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
  
    # 4. 记录日志
    log = SystemLog(
        user_id=user.id,
        action="login",
        module="auth"
    )
    db.add(log)
    db.commit()
  
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新个人信息"""
    if email:
        current_user.email = email
    if full_name:
        current_user.full_name = full_name
  
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 1. 验证旧密码
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(400, "Old password is incorrect")
  
    # 2. 更新密码
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
  
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """登出（客户端删除Token）"""
    return {"message": "Logged out successfully"}

注意：
- 所有错误要用HTTPException抛出
- 密码永远不要在响应中返回
- 每个操作都要记录到SystemLog
- Token过期时间设置为24小时
```

**测试命令**：

```bash
# 启动服务器
uvicorn app.main:app --reload

# 在另一个终端测试
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123"}'
```

---

## 🏥 Task 5: 实现医生数据API

### 命令给AI Agent：

```
请完善 backend/app/routers/doctors.py，实现所有医生数据接口：

要求：

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional

from app.database import get_db
from app.models import Doctor, PaymentRecord
from app.schemas import DoctorListResponse, DoctorResponse, DoctorStatistics
from app.core.security import get_current_active_user

router = APIRouter(prefix="/doctors", tags=["医生数据"])

@router.get("", response_model=DoctorListResponse)
async def get_doctors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    specialty: Optional[str] = None,
    state: Optional[str] = None,
    cluster_id: Optional[int] = None,
    min_monetary: Optional[float] = None,
    max_monetary: Optional[float] = None,
    search: Optional[str] = None,  # 搜索NPI或姓名
    sort_by: str = Query("rfm_monetary", regex="^(rfm_monetary|rfm_frequency|npi)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    分页查询医生列表，支持多条件筛选和排序
    """
    # 1. 构建基础查询
    query = db.query(Doctor)
  
    # 2. 应用筛选条件
    if specialty:
        query = query.filter(Doctor.specialty == specialty)
    if state:
        query = query.filter(Doctor.state == state)
    if cluster_id is not None:
        query = query.filter(Doctor.cluster_id == cluster_id)
    if min_monetary:
        query = query.filter(Doctor.rfm_monetary >= min_monetary)
    if max_monetary:
        query = query.filter(Doctor.rfm_monetary <= max_monetary)
    if search:
        query = query.filter(
            (Doctor.npi.contains(search)) |
            (Doctor.full_name.contains(search))
        )
  
    # 3. 应用排序
    sort_column = getattr(Doctor, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
  
    # 4. 分页
    total = query.count()
    doctors = query.offset((page - 1) * page_size).limit(page_size).all()
  
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": doctors
    }

@router.get("/{npi}", response_model=DoctorResponse)
async def get_doctor_detail(
    npi: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取医生详情"""
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(404, "Doctor not found")
  
    return doctor

@router.get("/statistics", response_model=DoctorStatistics)
async def get_statistics(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取医生数据统计"""
    # 1. 基础统计
    total_doctors = db.query(Doctor).count()
    total_monetary = db.query(func.sum(Doctor.rfm_monetary)).scalar() or 0.0
    avg_monetary = db.query(func.avg(Doctor.rfm_monetary)).scalar() or 0.0
    avg_frequency = db.query(func.avg(Doctor.rfm_frequency)).scalar() or 0.0
  
    # 2. 专业分布（Top 10）
    specialty_dist = db.query(
        Doctor.specialty,
        func.count(Doctor.npi).label('count')
    ).group_by(Doctor.specialty)\
     .order_by(func.count(Doctor.npi).desc())\
     .limit(10)\
     .all()
  
    # 3. 地区分布（Top 10）
    state_dist = db.query(
        Doctor.state,
        func.count(Doctor.npi).label('count')
    ).group_by(Doctor.state)\
     .order_by(func.count(Doctor.npi).desc())\
     .limit(10)\
     .all()
  
    # 4. 聚类分布
    cluster_dist = db.query(
        Doctor.cluster_id,
        Doctor.cluster_label,
        func.count(Doctor.npi).label('count')
    ).filter(Doctor.cluster_id.isnot(None))\
     .group_by(Doctor.cluster_id, Doctor.cluster_label)\
     .all()
  
    return {
        "total_doctors": total_doctors,
        "total_monetary": float(total_monetary),
        "avg_monetary": float(avg_monetary),
        "avg_frequency": float(avg_frequency),
        "specialty_distribution": {s[0]: s[1] for s in specialty_dist},
        "state_distribution": {s[0]: s[1] for s in state_dist},
        "cluster_distribution": {
            f"cluster_{c[0]}": {
                "label": c[1],
                "count": c[2]
            } for c in cluster_dist
        }
    }

@router.get("/options/specialties")
async def get_specialties(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有专业列表（用于筛选器）"""
    specialties = db.query(distinct(Doctor.specialty))\
        .filter(Doctor.specialty.isnot(None))\
        .order_by(Doctor.specialty)\
        .all()
  
    return {"specialties": [s[0] for s in specialties]}

@router.get("/options/states")
async def get_states(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有州列表（用于筛选器）"""
    states = db.query(distinct(Doctor.state))\
        .filter(Doctor.state.isnot(None))\
        .order_by(Doctor.state)\
        .all()
  
    return {"states": [s[0] for s in states]}

重要：
- 所有查询都要优化，避免N+1问题
- 分页参数要有合理的限制
- 统计查询要添加缓存（可选）
- 返回的数据要符合前端需要的格式
```

---

## 📊 Task 6: 实现分析服务

### 命令给AI Agent：

```
请创建 backend/app/services/analysis_service.py，实现K-Means聚类服务：

要求：

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.models import Doctor, ClusterResult, AnalysisTask

class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
  
    def perform_clustering(
        self,
        k: int,
        features: list[str] = None,
        task_name: str = "K-Means聚类"
    ) -> ClusterResult:
        """
        执行K-Means聚类分析
    
        Args:
            k: 聚类数量
            features: 使用的特征列表
            task_name: 任务名称
    
        Returns:
            ClusterResult对象
        """
        # 1. 加载数据
        doctors = self.db.query(Doctor).all()
        if not doctors:
            raise ValueError("No doctor data available")
    
        df = pd.DataFrame([{
            'npi': d.npi,
            'rfm_frequency': d.rfm_frequency or 0,
            'rfm_monetary': d.rfm_monetary or 0.0
        } for d in doctors])
    
        # 2. 准备特征
        if not features:
            features = ['rfm_frequency', 'rfm_monetary']
    
        X = df[features].values
    
        # 3. 处理异常值和标准化
        # 移除极端值（>99.9分位数）
        for i, feature in enumerate(features):
            percentile_999 = np.percentile(X[:, i], 99.9)
            X[:, i] = np.clip(X[:, i], 0, percentile_999)
    
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    
        # 4. 执行聚类
        kmeans = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        labels = kmeans.fit_predict(X_scaled)
        df['cluster'] = labels
    
        # 5. 计算评估指标
        silhouette = silhouette_score(X_scaled, labels)
        inertia = kmeans.inertia_
    
        # 6. 计算每个聚类的统计信息
        cluster_stats = {}
        cluster_labels_dict = {}
    
        for cluster_id in range(k):
            cluster_df = df[df['cluster'] == cluster_id]
        
            stats = {
                'size': len(cluster_df),
                'avg_frequency': float(cluster_df['rfm_frequency'].mean()),
                'median_frequency': float(cluster_df['rfm_frequency'].median()),
                'avg_monetary': float(cluster_df['rfm_monetary'].mean()),
                'median_monetary': float(cluster_df['rfm_monetary'].median()),
                'total_monetary': float(cluster_df['rfm_monetary'].sum())
            }
        
            # 自动生成标签
            label = self._generate_cluster_label(stats)
            cluster_labels_dict[str(cluster_id)] = label
        
            cluster_stats[str(cluster_id)] = {
                **stats,
                'label': label
            }
    
        # 7. 准备可视化数据（采样以减小数据量）
        sample_size = min(1000, len(df))
        sample_df = df.sample(n=sample_size, random_state=42)
    
        visualization_data = {
            'scatter_data': sample_df[[
                'rfm_frequency', 
                'rfm_monetary', 
                'cluster'
            ]].to_dict('records'),
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'radar_data': [
                {
                    'cluster': str(i),
                    'label': cluster_labels_dict[str(i)],
                    'frequency': cluster_stats[str(i)]['avg_frequency'],
                    'monetary': cluster_stats[str(i)]['avg_monetary']
                }
                for i in range(k)
            ]
        }
    
        # 8. 保存聚类结果
        result = ClusterResult(
            k_value=k,
            algorithm='k-means',
            features_used=json.dumps(features),
            cluster_stats=json.dumps(cluster_stats),
            cluster_labels=json.dumps(cluster_labels_dict),
            silhouette_score=float(silhouette),
            inertia=float(inertia),
            visualization_data=json.dumps(visualization_data),
            is_active=True,
            created_at=datetime.utcnow()
        )
    
        # 9. 更新doctors表的cluster_id和cluster_label
        for _, row in df.iterrows():
            self.db.query(Doctor).filter(Doctor.npi == row['npi']).update({
                'cluster_id': int(row['cluster']),
                'cluster_label': cluster_labels_dict[str(row['cluster'])]
            })
    
        # 10. 保存到数据库
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
    
        return result
  
    def _generate_cluster_label(self, stats: dict) -> str:
        """
        根据统计特征自动生成聚类标签
        """
        avg_monetary = stats['avg_monetary']
        avg_frequency = stats['avg_frequency']
    
        # 基于阈值的简单规则
        if avg_monetary > 10000 and avg_frequency > 20:
            return "顶级客户"
        elif avg_monetary > 5000:
            return "核心客户"
        elif avg_monetary > 1000:
            return "潜力客户"
        else:
            return "大众客户"
  
    def calculate_optimal_k(
        self,
        max_k: int = 10,
        features: list[str] = None
    ) -> dict:
        """
        使用Elbow方法确定最优K值
    
        Returns:
            包含inertia和silhouette分数的字典
        """
        # 加载数据
        doctors = self.db.query(Doctor).all()
        df = pd.DataFrame([{
            'rfm_frequency': d.rfm_frequency or 0,
            'rfm_monetary': d.rfm_monetary or 0.0
        } for d in doctors])
    
        if not features:
            features = ['rfm_frequency', 'rfm_monetary']
    
        X = df[features].values
    
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    
        # 计算不同K值的指标
        results = {}
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
        
            results[k] = {
                'inertia': float(kmeans.inertia_),
                'silhouette_score': float(silhouette_score(X_scaled, labels))
            }
    
        return results

注意：
- 使用标准化避免量级差异影响聚类
- 处理异常值（极端值裁剪）
- 可视化数据要采样，避免传输过大
- 聚类标签要有业务含义
```

---

## 🔗 Task 7: 实现分析API 

### 命令给AI Agent：

```
请完善 backend/app/routers/analysis.py，实现分析相关的所有接口：

要求：

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import ClusterResult, AnalysisTask
from app.schemas import (
    ClusteringRequest, 
    ClusterResultResponse,
    AnalysisTaskResponse
)
from app.services.analysis_service import AnalysisService
from app.core.security import get_current_active_user

router = APIRouter(prefix="/analysis", tags=["数据分析"])

def run_clustering_background(
    task_id: int,
    k: int,
    features: list[str],
    db: Session
):
    """后台任务：执行聚类"""
    task = db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
  
    try:
        # 更新状态
        task.status = "running"
        task.started_at = datetime.utcnow()
        db.commit()
    
        # 执行聚类
        service = AnalysisService(db)
        result = service.perform_clustering(k, features, task.task_name)
    
        # 更新任务状态
        task.status = "completed"
        task.progress = 100
        task.result_id = result.cluster_id
        task.completed_at = datetime.utcnow()
        db.commit()
    
    except Exception as e:
        task.status = "failed"
        task.error_message = str(e)
        db.commit()

@router.post("/perform", response_model=AnalysisTaskResponse)
async def perform_clustering(
    request: ClusteringRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    触发K-Means聚类分析（异步执行）
    """
    # 参数验证
    if request.k < 2 or request.k > 10:
        raise HTTPException(400, "K must be between 2 and 10")
  
    # 创建任务记录
    task = AnalysisTask(
        task_name=request.task_name,
        task_type="clustering",
        parameters=json.dumps({
            "k": request.k,
            "features": request.features
        }),
        status="pending",
        created_by=current_user.id
    )
  
    db.add(task)
    db.commit()
    db.refresh(task)
  
    # 添加后台任务
    background_tasks.add_task(
        run_clustering_background,
        task.task_id,
        request.k,
        request.features,
        db
    )
  
    return task

@router.get("/results", response_model=list[ClusterResultResponse])
async def get_all_cluster_results(
    limit: int = 10,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取所有聚类结果列表"""
    results = db.query(ClusterResult)\
        .order_by(ClusterResult.created_at.desc())\
        .limit(limit)\
        .all()
  
    return results

@router.get("/results/{cluster_id}", response_model=ClusterResultResponse)
async def get_cluster_result(
    cluster_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取指定聚类结果的详情"""
    result = db.query(ClusterResult)\
        .filter(ClusterResult.cluster_id == cluster_id)\
        .first()
  
    if not result:
        raise HTTPException(404, "Cluster result not found")
  
    # 解析JSON字段
    response_data = {
        "cluster_id": result.cluster_id,
        "k_value": result.k_value,
        "cluster_stats": json.loads(result.cluster_stats),
        "cluster_labels": json.loads(result.cluster_labels) if result.cluster_labels else {},
        "silhouette_score": result.silhouette_score,
        "inertia": result.inertia,
        "visualization_data": json.loads(result.visualization_data) if result.visualization_data else {},
        "created_at": result.created_at
    }
  
    return response_data

@router.get("/tasks/{task_id}/status", response_model=AnalysisTaskResponse)
async def get_task_status(
    task_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """查询分析任务状态"""
    task = db.query(AnalysisTask)\
        .filter(AnalysisTask.task_id == task_id)\
        .first()
  
    if not task:
        raise HTTPException(404, "Task not found")
  
    return task

@router.get("/optimal-k")
async def calculate_optimal_k(
    max_k: int = 10,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """计算最优K值（Elbow方法）"""
    service = AnalysisService(db)
    results = service.calculate_optimal_k(max_k)
  
    return {
        "results": results,
        "recommendation": "Based on elbow method, K=3 is recommended"
    }

注意：
- 聚类任务要异步执行，避免阻塞
- 提供任务状态查询接口
- JSON字段要正确解析后返回
- 添加适当的错误处理
```

---

## 📝 验收标准

完成以上所有任务后，应该满足：

✅ **数据库**：

- 7张表全部创建成功
- 索引正确建立
- 外键关系正确

✅ **认证系统**：

- 可以注册新用户
- 可以登录并获得JWT Token
- Token验证正常工作
- 可以获取当前用户信息

✅ **医生数据API**：

- 可以分页查询医生列表
- 筛选和排序功能正常
- 统计接口返回正确数据
- 专业和州列表接口正常

✅ **分析功能**：

- 可以触发K-Means聚类
- 聚类结果正确保存
- 可以查询聚类结果
- 可视化数据格式正确

✅ **文档**：

- Swagger文档完整
- 所有接口都有描述
- 可以在线测试

---

## 🎯 下一步

完成Phase 1后，你可以：

1. 前端对接这些新API
2. 开始Phase 3的Dify集成
3. 实现报告生成功能

有任何问题随时反馈！
