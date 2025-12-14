"""
FastAPI Main Application Entry Point.

医药市场画像与策略生成系统 - Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .config import get_settings
from . import models  # Import models to ensure tables are created

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    description="基于多智能体的医药市场画像与策略生成系统 API",
    version="0.1.0",
    debug=settings.debug
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "医药市场画像与策略生成系统 API 运行中",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "app_name": settings.app_name
    }


from .routers import analysis_tasks, auth, doctors, reports

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(doctors.router, prefix="/api/v1/doctors", tags=["doctors"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(analysis_tasks.router, prefix="/api/v1/analysis/tasks", tags=["analysis-tasks"])
