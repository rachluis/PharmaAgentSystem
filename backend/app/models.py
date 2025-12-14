"""
SQLAlchemy ORM Models for Pharma Market Analysis System.

Tables:
- User: System users with authentication
- Doctor: Aggregated doctor profiles with RFM values
- PaymentRecord: Cleaned payment records from CMS Open Payments
- ClusterResult: K-Means clustering results for AI strategy generation
"""
from datetime import date, datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """User table for authentication and authorization."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="viewer")  # admin / analyst / viewer
    avatar_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    analysis_tasks = relationship("AnalysisTask", back_populates="creator")
    ai_reports = relationship("AIReport", back_populates="creator")
    system_logs = relationship("SystemLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Doctor(Base):
    """
    Doctor profile table - stores aggregated doctor information and RFM values.
    Primary key is NPI (National Provider Identifier).
    """
    __tablename__ = "doctors"
    
    # Primary identifier
    npi = Column(String(10), primary_key=True, index=True, comment="National Provider Identifier")
    
    # Basic information
    first_name = Column(String(100), nullable=True, comment="医生名")
    last_name = Column(String(100), nullable=True, comment="医生姓")
    full_name = Column(String(200), nullable=True, comment="全名 (first_name + last_name)")
    primary_type = Column(String(100), nullable=True, comment="医生类型 (Medical Doctor, DO, etc.)")
    specialty = Column(String(200), nullable=True, comment="专科分类")
    state = Column(String(10), nullable=True, comment="所在州")
    city = Column(String(100), nullable=True, comment="城市")
    
    # RFM Values (computed from PaymentRecords)
    recency_days = Column(Integer, nullable=True, comment="最近支付距今天数 (R值)")
    frequency = Column(Integer, nullable=True, comment="支付记录次数 (F值)")
    monetary = Column(Float, nullable=True, comment="累计支付总金额 (M值)")
    
    # Additional aggregated metrics
    total_payments = Column(Integer, default=0, comment="支付记录总数")
    avg_payment_amount = Column(Float, default=0.0, comment="平均单笔支付金额")
    last_payment_date = Column(Date, nullable=True, comment="最近支付日期")
    
    # Clustering result
    cluster_id = Column(Integer, ForeignKey("cluster_results.cluster_id"), nullable=True)
    cluster_label = Column(String(50), nullable=True, comment="聚类标签 (如: 核心客户)")
    
    # Relationships
    payments = relationship("PaymentRecord", back_populates="doctor")
    cluster = relationship("ClusterResult", back_populates="doctors")
    
    def __repr__(self):
        return f"<Doctor(npi={self.npi}, name={self.first_name} {self.last_name})>"


class PaymentRecord(Base):
    """
    Payment record table - stores cleaned records from CMS Open Payments.
    Each record represents a single payment/transfer of value.
    """
    __tablename__ = "payment_records"
    
    # Primary key (auto-increment)
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to Doctor
    npi = Column(String(10), ForeignKey("doctors.npi"), index=True, nullable=False)
    
    # Payment details
    amount = Column(Float, nullable=False, comment="支付金额 (USD)")
    payment_date = Column(Date, nullable=False, comment="支付日期")
    payment_type = Column(String(100), nullable=True, comment="支付类型 (Nature_of_Payment)")
    
    # Manufacturer/Product info
    manufacturer_name = Column(String(200), nullable=True, comment="药企名称")
    product_name = Column(String(200), nullable=True, comment="产品名称")
    
    # Relationship
    doctor = relationship("Doctor", back_populates="payments")
    
    def __repr__(self):
        return f"<PaymentRecord(id={self.id}, npi={self.npi}, amount={self.amount})>"


class ClusterResult(Base):
    """
    Cluster result table - stores K-Means clustering analysis results.
    Used to provide context for Dify AI strategy generation.
    """
    __tablename__ = "cluster_results"
    
    # Primary key
    cluster_id = Column(Integer, primary_key=True, comment="聚类编号")
    
    # Cluster metadata
    cluster_name = Column(String(100), nullable=True, comment="聚类名称 (如: 高价值核心客户)")
    size_count = Column(Integer, nullable=True, comment="该聚类医生数量")
    size_percentage = Column(Float, nullable=True, comment="占总医生百分比")
    
    # Analysis metadata
    task_id = Column(Integer, ForeignKey("analysis_tasks.task_id"), nullable=True, comment="关联的分析任务ID")
    algorithm = Column(String(50), default="k-means", comment="聚类算法")
    features_used = Column(Text, nullable=True, comment="使用的特征列表 (JSON)")
    cluster_labels = Column(Text, nullable=True, comment="聚类标签映射 (JSON)")
    
    # Quality metrics
    silhouette_score = Column(Float, nullable=True, comment="轮廓系数")
    inertia = Column(Float, nullable=True, comment="簇内误差平方和")
    
    # KPI Summary (JSON structure for AI consumption)
    # Example: {"Avg_R_Days": 30, "Avg_F_Count": 50, "Avg_M_Amount": 15000.0, "Top_Specialty": "心血管内科"}
    kpi_summary = Column(JSON, nullable=True, comment="聚类 KPI 摘要 (JSON)")
    
    # Strategy focus (human-readable or AI-generated)
    strategy_focus = Column(Text, nullable=True, comment="策略建议")
    
    # Context for LLM (additional info for Dify)
    context_for_llm = Column(Text, nullable=True, comment="给 AI 的补充上下文")
    
    # Visualization and status
    visualization_data = Column(Text, nullable=True, comment="可视化数据 (JSON)")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # Relationships
    doctors = relationship("Doctor", back_populates="cluster")
    task = relationship("AnalysisTask", back_populates="result")
    
    def __repr__(self):
        return f"<ClusterResult(id={self.cluster_id}, name={self.cluster_name})>"


class AnalysisTask(Base):
    """
    Analysis task table - tracks K-Means clustering and RFM analysis jobs.
    Enables async task execution and progress monitoring.
    """
    __tablename__ = "analysis_tasks"
    
    # Primary key
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Task metadata
    task_name = Column(String(200), nullable=False, comment="任务名称")
    task_type = Column(String(50), nullable=False, comment="任务类型 (clustering, rfm_analysis)")
    parameters = Column(Text, nullable=True, comment="任务参数 (JSON)")
    
    # Status tracking
    status = Column(String(20), default="pending", comment="状态: pending/running/completed/failed")
    progress = Column(Integer, default=0, comment="进度 (0-100)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # User and timing
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Result reference
    result_id = Column(Integer, ForeignKey("cluster_results.cluster_id"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="analysis_tasks")
    result = relationship("ClusterResult", back_populates="task")
    
    def __repr__(self):
        return f"<AnalysisTask(id={self.task_id}, name={self.task_name}, status={self.status})>"


class AIReport(Base):
    """
    AI report table - stores Dify-generated market strategy reports.
    Supports Markdown content and metadata for report management.
    """
    __tablename__ = "ai_reports"
    
    # Primary key
    report_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Report content
    report_title = Column(String(300), nullable=False, comment="报告标题")
    report_type = Column(String(50), nullable=False, comment="报告类型 (cluster_analysis, doctor_profile)")
    report_content = Column(Text, nullable=False, comment="报告内容 (Markdown)")
    report_summary = Column(Text, nullable=True, comment="报告摘要")
    
    # Related entities
    related_cluster_id = Column(Integer, ForeignKey("cluster_results.cluster_id"), nullable=True)
    related_npi = Column(String(20), ForeignKey("doctors.npi"), nullable=True)
    
    # Generation metadata
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    dify_conversation_id = Column(String(100), nullable=True, comment="Dify对话ID")
    generation_time = Column(Float, nullable=True, comment="生成耗时 (秒)")
    
    # Publishing status
    status = Column(String(20), default="draft", comment="状态: draft/published/archived")
    view_count = Column(Integer, default=0, comment="查看次数")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cluster = relationship("ClusterResult")
    doctor = relationship("Doctor")
    creator = relationship("User", back_populates="ai_reports")
    
    def __repr__(self):
        return f"<AIReport(id={self.report_id}, title={self.report_title})>"


class SystemLog(Base):
    """
    System log table - audit trail for all API operations.
    Used for security monitoring, debugging, and usage analytics.
    """
    __tablename__ = "system_logs"
    
    # Primary key
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User and action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False, comment="操作名称 (login, register, run_clustering)")
    module = Column(String(50), nullable=False, comment="模块名称 (auth, analysis, reports)")
    
    # Request details
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    request_data = Column(Text, nullable=True, comment="请求数据 (JSON)")
    response_status = Column(Integer, nullable=True, comment="HTTP状态码")
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", back_populates="system_logs")
    
    def __repr__(self):
        return f"<SystemLog(id={self.log_id}, action={self.action}, user_id={self.user_id})>"
