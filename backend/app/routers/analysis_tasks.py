from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
import json

from ..database import get_db
from ..models import AnalysisTask, User
from ..schemas import AnalysisTaskCreate, AnalysisTaskResponse
from ..core.security import get_current_active_user
from ..services.analysis_service import analysis_service
from ..services.analysis_service_optimized import optimized_analysis_service

router = APIRouter()  # Remove prefix here, it's added in main.py

@router.post("", response_model=AnalysisTaskResponse)
async def create_analysis_task(
    task_in: AnalysisTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new analysis task (e.g., Clustering).
    The task will be executed in the background.
    """
    # 1. Create Task Record
    db_task = AnalysisTask(
        task_name=task_in.task_name,
        task_type=task_in.task_type,
        parameters=json.dumps(task_in.parameters) if task_in.parameters else None,
        status="pending",
        created_by=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 2. Trigger Background Task
    if task_in.task_type == "clustering":
        # 使用优化后的聚类服务（支持缓存、MiniBatchKMeans、Recency反转）
        use_optimized = task_in.parameters.get('use_optimized', True) if task_in.parameters else True

        if use_optimized:
            background_tasks.add_task(
                optimized_analysis_service.perform_clustering,
                db,
                db_task.task_id,
                use_cache=True  # 启用缓存
            )
        else:
            # 使用原始服务（用于对比测试）
            background_tasks.add_task(
                analysis_service.perform_clustering,
                db,
                db_task.task_id
            )
    
    # Note: Operation logging is now handled by middleware
    
    return db_task

@router.get("", response_model=dict)
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List analysis tasks with pagination.
    """
    query = db.query(AnalysisTask)
    
    if status:
        query = query.filter(AnalysisTask.status == status)
        
    total = query.count()
    tasks = query.order_by(desc(AnalysisTask.created_at))\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
        
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": tasks
    }

# ========================================
# 重要：具体路由必须放在通用路由之前！
# ========================================
from ..models import ClusterResult
from ..schemas import ClusterResultResponse

@router.get("/results", response_model=List[ClusterResultResponse])
async def get_clustering_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active clustering results.

    路径: GET /api/v1/analysis/tasks/results
    返回: 所有激活的聚类结果列表
    """
    results = db.query(ClusterResult).filter(ClusterResult.is_active == True).order_by(desc(ClusterResult.cluster_id)).all()
    return results

# ========================================
# 通用路由放在后面，避免路径冲突
# ========================================

@router.get("/{task_id}", response_model=AnalysisTaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get task details by ID.
    """
    task = db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    """
    task = db.query(AnalysisTask).filter(AnalysisTask.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
