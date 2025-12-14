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
    primary_type = Column(String(100), nullable=True, comment="医生类型 (Medical Doctor, DO, etc.)")
    specialty = Column(String(200), nullable=True, comment="专科分类")
    state = Column(String(10), nullable=True, comment="所在州")
    
    # RFM Values (computed from PaymentRecords)
    recency_days = Column(Integer, nullable=True, comment="最近支付距今天数 (R值)")
    frequency = Column(Integer, nullable=True, comment="支付记录次数 (F值)")
    monetary = Column(Float, nullable=True, comment="累计支付总金额 (M值)")
    
    # Clustering result
    cluster_id = Column(Integer, ForeignKey("cluster_results.cluster_id"), nullable=True)
    
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
    
    # KPI Summary (JSON structure for AI consumption)
    # Example: {"Avg_R_Days": 30, "Avg_F_Count": 50, "Avg_M_Amount": 15000.0, "Top_Specialty": "心血管内科"}
    kpi_summary = Column(JSON, nullable=True, comment="聚类 KPI 摘要 (JSON)")
    
    # Strategy focus (human-readable or AI-generated)
    strategy_focus = Column(Text, nullable=True, comment="策略建议")
    
    # Context for LLM (additional info for Dify)
    context_for_llm = Column(Text, nullable=True, comment="给 AI 的补充上下文")
    
    # Relationship
    doctors = relationship("Doctor", back_populates="cluster")
    
    def __repr__(self):
        return f"<ClusterResult(id={self.cluster_id}, name={self.cluster_name})>"
