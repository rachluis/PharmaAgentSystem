# PharmaAgent System - Backend

基于 FastAPI 的医药市场分析系统后端服务。

## 🛠️ 技术栈

- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: JWT (OAuth2)
- **Data Processing**: Pandas, Scikit-learn (K-Means Clustering)
- **Task Queue**: FastAPI BackgroundTasks

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.8+。

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

*如果 `requirements.txt` 不存在或已过时，请安装以下核心包：*

```powershell
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt pandas scikit-learn requests python-multipart
```

### 3. 初始化数据库

运行脚本初始化数据库表结构（包括用户、医生、日志等）：

```powershell
$env:PYTHONPATH="."
python scripts/init_db.py
python scripts/create_log_tables.py
```

### 4. 启动服务

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

服务启动后，可访问：

- **API 文档**: <http://127.0.0.1:8000/docs>
- **静态文件**: <http://127.0.0.1:8000/uploads>

## 📂 目录结构

- `app/`: 应用核心代码
  - `models.py`: 数据库模型
  - `routers/`: API 路由 (Auth, Doctors, Analysis, System)
  - `core/`: 核心配置与中间件 (Security, Logging)
- `scripts/`: 维护脚本 (DB Init, Test Scripts)
- `uploads/`: 用户上传文件 (Avatars)
