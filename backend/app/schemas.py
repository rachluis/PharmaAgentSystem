"""
Pydantic schemas for API request/response validation.
"""
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============== Doctor Schemas ==============

class DoctorBase(BaseModel):
    """Base doctor schema with common fields."""
    npi: str = Field(..., description="National Provider Identifier")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_type: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None


class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor."""
    pass


class DoctorRFM(BaseModel):
    """RFM values for a doctor."""
    recency_days: Optional[int] = Field(None, description="最近支付距今天数")
    frequency: Optional[int] = Field(None, description="支付记录次数")
    monetary: Optional[float] = Field(None, description="累计支付总金额")


class DoctorResponse(DoctorBase):
    """Full doctor response including RFM and cluster."""
    recency_days: Optional[int] = None
    frequency: Optional[int] = None
    monetary: Optional[float] = None
    cluster_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class DoctorList(BaseModel):
    """Paginated list of doctors."""
    total: int
    items: List[DoctorResponse]


# ============== Payment Schemas ==============

class PaymentRecordBase(BaseModel):
    """Base payment record schema."""
    npi: str
    amount: float
    payment_date: date
    payment_type: Optional[str] = None
    manufacturer_name: Optional[str] = None
    product_name: Optional[str] = None


class PaymentRecordCreate(PaymentRecordBase):
    """Schema for creating a payment record."""
    pass


class PaymentRecordResponse(PaymentRecordBase):
    """Payment record response with ID."""
    id: int
    
    class Config:
        from_attributes = True


# ============== Cluster Schemas ==============

class ClusterKPISummary(BaseModel):
    """KPI summary structure for a cluster."""
    Avg_R_Days: Optional[float] = None
    Avg_F_Count: Optional[float] = None
    Avg_M_Amount: Optional[float] = None
    Top_Specialty: Optional[str] = None
    Top_Manufacturer: Optional[str] = None


class ClusterResultBase(BaseModel):
    """Base cluster result schema."""
    cluster_id: int
    cluster_name: Optional[str] = None
    size_count: Optional[int] = None
    size_percentage: Optional[float] = None
    kpi_summary: Optional[Dict[str, Any]] = None
    strategy_focus: Optional[str] = None
    context_for_llm: Optional[str] = None


class ClusterResultCreate(ClusterResultBase):
    """Schema for creating a cluster result."""
    pass


class ClusterResultResponse(ClusterResultBase):
    """Cluster result response."""
    class Config:
        from_attributes = True


# ============== Analysis Schemas ==============

class ClusteringRequest(BaseModel):
    """Request schema for running K-Means clustering."""
    k: int = Field(default=5, ge=2, le=10, description="Number of clusters (K value)")
    features: List[str] = Field(
        default=["recency_days", "frequency", "monetary"],
        description="Features to use for clustering"
    )


class ClusteringResponse(BaseModel):
    """Response after clustering is complete."""
    success: bool
    message: str
    clusters: List[ClusterResultResponse]
