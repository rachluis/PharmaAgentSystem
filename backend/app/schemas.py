"""
Pydantic schemas for API request/response validation.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


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


class DoctorUpdate(BaseModel):
    """Schema for updating doctor details (NPI excluded)."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    primary_type: Optional[str] = None
    specialty: Optional[str] = None
    state: Optional[str] = None


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
    
    # Analysis metadata
    task_id: Optional[int] = None
    algorithm: Optional[str] = None
    features_used: Optional[Any] = None  # Will be parsed from JSON
    cluster_labels: Optional[Dict[str, str]] = None  # Will be parsed from JSON
    
    # Quality metrics
    silhouette_score: Optional[float] = None
    inertia: Optional[float] = None
    
    # KPI and strategy
    kpi_summary: Optional[Dict[str, Any]] = None  # Will be parsed from JSON
    strategy_focus: Optional[str] = None
    context_for_llm: Optional[str] = None
    
    # Visualization
    visualization_data: Optional[Any] = None  # Will be parsed from JSON
    is_active: Optional[bool] = None


class ClusterResultCreate(ClusterResultBase):
    """Schema for creating a cluster result."""
    pass


class ClusterResultResponse(ClusterResultBase):
    """Cluster result response."""
    
    @field_validator('kpi_summary', 'cluster_labels', 'features_used', 'visualization_data', mode='before')
    @classmethod
    def parse_json_fields(cls, v):
        """Parse JSON string fields to dict/list if needed."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return None
        return v
    
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


# ============== Analysis Task Schemas ==============

class AnalysisTaskBase(BaseModel):
    task_name: str
    task_type: str = "clustering"
    parameters: Optional[Dict[str, Any]] = None

class AnalysisTaskCreate(AnalysisTaskBase):
    pass

class AnalysisTaskResponse(AnalysisTaskBase):
    task_id: int
    status: str
    progress: int
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    result_id: Optional[int] = None
    
    @field_validator('parameters', mode='before')
    @classmethod
    def parse_parameters(cls, v):
        """Parse JSON string to dict if needed."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except:
                return None
        return v
    
    class Config:
        from_attributes = True


# ============== AI Report Schemas ==============

class AIReportBase(BaseModel):
    report_title: str
    report_type: str
    report_summary: Optional[str] = None
    related_cluster_id: Optional[int] = None
    related_npi: Optional[str] = None

class AIReportCreate(AIReportBase):
    report_content: Optional[str] = "" # Optional on create, filled by AI
    dify_conversation_id: Optional[str] = None

class AIReportResponse(AIReportBase):
    report_id: int
    report_content: str
    generated_by: int
    dify_conversation_id: Optional[str] = None
    generation_time: Optional[float] = None
    status: str
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True



class AIReportList(BaseModel):
    total: int
    items: List[AIReportResponse]
