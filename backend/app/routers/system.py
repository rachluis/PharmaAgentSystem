from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import LoginLog, OperationLog
from app.core.security import get_current_active_user, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Schemas
class LoginLogSchema(BaseModel):
    id: int
    username: str
    ip_address: Optional[str]
    browser: Optional[str]
    os: Optional[str]
    status: int
    message: Optional[str]
    login_time: datetime

    class Config:
        from_attributes = True

class OperationLogSchema(BaseModel):
    id: int
    username: Optional[str]
    module: Optional[str]
    summary: Optional[str]
    method: str
    path: str
    status: Optional[int]
    latency_ms: Optional[int]
    create_time: datetime

    class Config:
        from_attributes = True

class PaginatedLoginLogs(BaseModel):
    total: int
    items: List[LoginLogSchema]

class PaginatedOpLogs(BaseModel):
    total: int
    items: List[OperationLogSchema]


@router.get("/logs/login", response_model=PaginatedLoginLogs)
def get_login_logs(
    page: int = 1,
    size: int = 20,
    username: Optional[str] = None,
    status: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get login logs table."""
    query = db.query(LoginLog)
    
    if username:
        query = query.filter(LoginLog.username.ilike(f"%{username}%"))
    if status is not None:
        query = query.filter(LoginLog.status == status)
        
    total = query.count()
    items = query.order_by(desc(LoginLog.login_time))\
        .offset((page - 1) * size)\
        .limit(size)\
        .all()
        
    return {"total": total, "items": items}


@router.get("/logs/operation", response_model=PaginatedOpLogs)
def get_operation_logs(
    page: int = 1,
    size: int = 20,
    module: Optional[str] = None,
    username: Optional[str] = None,
    method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get operation logs table."""
    query = db.query(OperationLog)
    
    if module:
        query = query.filter(OperationLog.module == module)
    if username:
        query = query.filter(OperationLog.username.ilike(f"%{username}%"))
    if method:
        query = query.filter(OperationLog.method == method)
        
    total = query.count()
    items = query.order_by(desc(OperationLog.create_time))\
        .offset((page - 1) * size)\
        .limit(size)\
        .all()
        
    return {"total": total, "items": items}
