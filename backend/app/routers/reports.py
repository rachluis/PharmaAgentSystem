from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import time

from ..database import get_db
from ..models import User, AIReport, ClusterResult, Doctor
from ..schemas import AIReportResponse, AIReportCreate, AIReportList
from ..core.security import get_current_user
from ..services.dify_service import dify_service

router = APIRouter()


class GenerateStrategyRequest(BaseModel):
    cluster_id: int
    user_prompt: Optional[str] = None


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


@router.post("/generate-stream")
async def generate_strategy_stream(
    request: GenerateStrategyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI strategy report with SSE streaming.
    Returns text/event-stream for real-time display.
    """
    # Get cluster result
    cluster = db.query(ClusterResult).filter(ClusterResult.cluster_id == request.cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Prepare cluster statistics as JSON string
    cluster_stats_json = dify_service.prepare_cluster_stats(cluster)
    
    async def event_generator():
        start_time = time.time()
        full_content = []
        
        async for chunk in dify_service.stream_chat(
            cluster_stats=cluster_stats_json,
            user_intent=request.user_prompt or "",
            user_id=str(current_user.id)
        ):
            full_content.append(chunk)
            yield f"data: {chunk}\n\n"
        
        # Signal end
        yield "data: [DONE]\n\n"
        
        # Save report (non-streaming, after completion)
        generation_time = time.time() - start_time
        dify_service.save_report(
            db=db,
            title=f"AI策略报告 - Cluster {request.cluster_id}",
            content="".join(full_content),
            cluster_id=request.cluster_id,
            user_id=current_user.id,
            user_prompt=request.user_prompt,
            generation_time=generation_time
        )
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.post("/generate", status_code=201)
async def generate_report_sync(
    request: AIReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and save an AI report (non-streaming, synchronous).
    """
    # Get cluster result if related
    cluster = None
    cluster_stats_json = ""
    if request.related_cluster_id:
        cluster = db.query(ClusterResult).filter(ClusterResult.cluster_id == request.related_cluster_id).first()
        if cluster:
            cluster_stats_json = dify_service.prepare_cluster_stats(cluster)
    
    # Generate content (collect all chunks)
    content_parts = []
    async for chunk in dify_service.stream_chat(
        cluster_stats=cluster_stats_json,
        user_intent="",
        user_id=str(current_user.id)
    ):
        content_parts.append(chunk)
    
    content = "".join(content_parts)
    
    # Save report
    report = dify_service.save_report(
        db=db,
        title=request.report_title,
        content=content,
        cluster_id=request.related_cluster_id or 0,
        user_id=current_user.id,
        generation_time=0.0
    )
    
    return {
        "code": 201,
        "message": "Report generated successfully",
        "report_id": report.report_id
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
