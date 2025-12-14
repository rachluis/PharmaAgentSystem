"""
Reports API Router.
Handles AI report generation, listing, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..models import User, AIReport, ClusterResult, Doctor
from ..schemas import AIReportResponse, AIReportCreate, AIReportList
from ..core.security import get_current_user
from ..services.dify_service import dify_service

router = APIRouter()

@router.get("", response_model=AIReportList)
async def get_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of reports.
    """
    query = db.query(AIReport)
    
    if report_type:
        query = query.filter(AIReport.report_type == report_type)
    if status:
        query = query.filter(AIReport.status == status)
        
    total = query.count()
    items = query.order_by(desc(AIReport.created_at))\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "total": total,
        "items": items
    }


@router.get("/{report_id}", response_model=AIReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed report by ID.
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Increment view count
    report.view_count += 1
    db.commit()
    
    return report


@router.post("/generate", status_code=201)
async def generate_report(
    request: AIReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new AI report (async task).
    Returns report_id immediately, actual generation happens in background.
    """
    # Create new report record
    new_report = AIReport(
        report_title=request.report_title,
        report_type=request.report_type,
        report_content="正在生成中...",
        status="generating",
        generated_by=current_user.id,
        related_cluster_id=request.related_cluster_id,
        related_npi=request.related_npi,
        dify_conversation_id=request.dify_conversation_id
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Trigger Background Task
    background_tasks.add_task(dify_service.generate_report, db, new_report.report_id)
    
    return {
        "code": 201,
        "message": "Report generation started",
        "report_id": new_report.report_id
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
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = "archived"
    db.commit()
    
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
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # In a real app, generate file here
    return {
        "code": 200,
        "message": f"Download link for {format} format",
        "download_url": f"/api/v1/reports/{report_id}/files/{format}" # Placeholder
    }
