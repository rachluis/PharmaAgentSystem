"""
Reports API Router.
Handles AI report generation, listing, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from ..database import get_db
from ..models import User
from ..core.security import get_current_user

router = APIRouter()


# ============== Enums ==============

class ReportType(str, Enum):
    cluster_analysis = "cluster_analysis"
    doctor_profile = "doctor_profile"
    market_strategy = "market_strategy"


class ReportStatus(str, Enum):
    draft = "draft"
    generating = "generating"
    published = "published"
    archived = "archived"


# ============== Schemas ==============

class ReportCreate(BaseModel):
    report_type: ReportType
    cluster_id: Optional[int] = None
    custom_prompt: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: int
    report_title: str
    report_type: str
    status: str
    content: Optional[str] = None
    created_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    total: int
    items: List[ReportResponse]


# ============== Mock Data (临时) ==============

mock_reports = [
    {
        "report_id": 1,
        "report_title": "2024 Q4 医生聚类分析报告",
        "report_type": "cluster_analysis",
        "status": "published",
        "content": "# 医生聚类分析报告\n\n## 执行摘要\n本次聚类分析共识别出5个不同特征的医生群体...",
        "created_at": datetime(2024, 12, 10, 10, 30),
        "created_by": 1
    },
    {
        "report_id": 2,
        "report_title": "高价值医生画像报告",
        "report_type": "doctor_profile",
        "status": "published",
        "content": "# 高价值医生画像\n\n## Cluster 0 分析\n该群体共计15,234名医生，占总数的2.06%...",
        "created_at": datetime(2024, 12, 12, 14, 20),
        "created_by": 1
    }
]

report_id_counter = 3


# ============== Endpoints ==============

@router.get("", response_model=ReportListResponse)
async def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of reports.
    """
    # Filter reports
    filtered_reports = mock_reports
    if report_type:
        filtered_reports = [r for r in filtered_reports if r["report_type"] == report_type]
    if status:
        filtered_reports = [r for r in filtered_reports if r["status"] == status]
    
    total = len(filtered_reports)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered_reports[start:end]
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed report by ID.
    """
    report = next((r for r in mock_reports if r["report_id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/generate")
async def generate_report(
    request: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new AI report (async task).
    Returns report_id immediately, actual generation happens in background.
    """
    global report_id_counter
    
    # Create new report
    new_report = {
        "report_id": report_id_counter,
        "report_title": f"{request.report_type.value} Report #{report_id_counter}",
        "report_type": request.report_type.value,
        "status": "generating",
        "content": "正在生成中...",
        "created_at": datetime.now(),
        "created_by": current_user.id
    }
    
    mock_reports.insert(0, new_report)
    report_id_counter += 1
    
    # TODO: 实际应该触发异步任务调用 Dify API
    # from ..services.dify_service import generate_report_async
    # background_tasks.add_task(generate_report_async, report_id, request)
    
    return {
        "code": 201,
        "message": "Report generation started",
        "report_id": new_report["report_id"]
    }


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a report (soft delete by changing status to archived).
    """
    report = next((r for r in mock_reports if r["report_id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Soft delete
    report["status"] = "archived"
    
    return {"code": 200, "message": "Report archived successfully"}


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query("markdown", regex="^(markdown|pdf|docx)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download report in specified format.
    """
    report = next((r for r in mock_reports if r["report_id"] == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # TODO: Implement actual file generation
    return {
        "code": 200,
        "message": f"Download link for {format} format",
        "download_url": f"/reports/{report_id}/files/{format}"
    }
