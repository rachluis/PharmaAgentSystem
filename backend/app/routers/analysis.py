"""
API Router for Analysis and Clustering.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import ClusteringRequest, ClusteringResponse, ClusterResultResponse
from ..models import ClusterResult
from ..services.analysis_service import analysis_service

router = APIRouter()

@router.post("/perform", response_model=ClusteringResponse)
async def perform_clustering(
    request: ClusteringRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger K-Means clustering analysis.
    This is a long-running operation, so it might run in background in production.
    For this demo, we run it synchronously to return immediate results.
    """
    try:
        result = analysis_service.perform_clustering(
            db=db, 
            k=request.k, 
            features=request.features
        )
        
        # Fetch created results
        clusters = db.query(ClusterResult).all()
        
        return {
            "success": True, 
            "message": f"Clustering completed with K={request.k}",
            "clusters": clusters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-strategies")
async def generate_strategies(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger AI Strategy Generation (Mock/Dify).
    Updates the 'strategy_focus' field in cluster_results.
    """
    try:
        # Run synchronously for now to see immediate results
        count = analysis_service.generate_ai_strategies(db)
        return {
            "success": True, 
            "message": f"Generated strategies for {count} clusters."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results", response_model=List[ClusterResultResponse])
async def get_clustering_results(db: Session = Depends(get_db)):
    """
    Get existing clustering results for visualization.
    """
    results = db.query(ClusterResult).order_by(ClusterResult.cluster_id).all()
    if not results:
        return []
    return results
