"""
Doctors API Router.
Handles doctor data queries, statistics, and details.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from pydantic import BaseModel

from ..database import get_db
from ..models import Doctor, PaymentRecord
from ..core.security import get_current_user
from ..schemas import DoctorResponse, DoctorList, PaymentRecordResponse, DoctorCreate, DoctorUpdate

router = APIRouter()


# ============== Response Models ==============

class DoctorStatistics(BaseModel):
    total_doctors: int
    total_monetary: float
    avg_monetary: float
    avg_frequency: float
    specialty_distribution: dict
    state_distribution: dict


class DoctorDetailResponse(BaseModel):
    doctor: DoctorResponse
    recent_payments: List[PaymentRecordResponse]


# ============== Endpoints ==============

@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(doctor: DoctorCreate, db: Session = Depends(get_db)):
    """Create a new doctor profile."""
    # Check if NPI exists
    existing_doctor = db.query(Doctor).filter(Doctor.npi == doctor.npi).first()
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Doctor with NPI {doctor.npi} already exists."
        )
    
    # Create new doctor
    new_doctor = Doctor(
        npi=doctor.npi,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        full_name=f"{doctor.first_name} {doctor.last_name}".strip(),
        specialty=doctor.specialty,
        state=doctor.state,
        city=None, # Not in schema yet
        primary_type=doctor.primary_type,
        # Default stats
        monetary=0.0,
        frequency=0,
        recency_days=None
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor


@router.put("/{npi}", response_model=DoctorResponse)
async def update_doctor(npi: str, doctor_update: DoctorUpdate, db: Session = Depends(get_db)):
    """Update doctor details."""
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Update fields if provided
    if doctor_update.first_name is not None:
        doctor.first_name = doctor_update.first_name
    if doctor_update.last_name is not None:
        doctor.last_name = doctor_update.last_name
    
    # Re-compute full name if names changed
    if doctor_update.first_name is not None or doctor_update.last_name is not None:
        doctor.full_name = f"{doctor.first_name} {doctor.last_name}".strip()

    if doctor_update.specialty is not None:
        doctor.specialty = doctor_update.specialty
    if doctor_update.state is not None:
        doctor.state = doctor_update.state
    if doctor_update.primary_type is not None:
        doctor.primary_type = doctor_update.primary_type
        
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{npi}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(npi: str, db: Session = Depends(get_db)):
    """Delete a doctor profile."""
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Optional: Check for related records logic or cascade delete
    # For now, we rely on DB cascade or allow deletion
    db.delete(doctor)
    db.commit()
    return None

@router.get("", response_model=DoctorList)
async def get_doctors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    state: Optional[str] = Query(None, description="Filter by state"),
    cluster_id: Optional[int] = Query(None, description="Filter by cluster ID"),
    min_monetary: Optional[float] = Query(None, description="Minimum monetary value"),
    max_monetary: Optional[float] = Query(None, description="Maximum monetary value"),
    search: Optional[str] = Query(None, description="Search by name or NPI"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of doctors with optional filters.
    """
    query = db.query(Doctor)
    
    # Apply filters
    if specialty:
        query = query.filter(Doctor.specialty == specialty)
    if state:
        query = query.filter(Doctor.state == state)
    if cluster_id is not None:
        query = query.filter(Doctor.cluster_id == cluster_id)
    if min_monetary is not None:
        query = query.filter(Doctor.monetary >= min_monetary)
    if max_monetary is not None:
        query = query.filter(Doctor.monetary <= max_monetary)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Doctor.npi.ilike(search_pattern)) |
            (Doctor.first_name.ilike(search_pattern)) |
            (Doctor.last_name.ilike(search_pattern))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by monetary desc
    doctors = query.order_by(Doctor.monetary.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "total": total,
        "items": doctors
    }


@router.get("/statistics", response_model=DoctorStatistics)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get aggregate statistics for all doctors.
    """
    # Basic stats
    total_doctors = db.query(Doctor).count()
    total_monetary = db.query(func.sum(Doctor.monetary)).scalar() or 0
    avg_monetary = db.query(func.avg(Doctor.monetary)).scalar() or 0
    avg_frequency = db.query(func.avg(Doctor.frequency)).scalar() or 0
    
    # Specialty distribution (top 10)
    specialty_dist = db.query(
        Doctor.specialty,
        func.count(Doctor.npi).label('count')
    ).filter(Doctor.specialty.isnot(None))\
        .group_by(Doctor.specialty)\
        .order_by(func.count(Doctor.npi).desc())\
        .limit(10)\
        .all()
    
    # State distribution (top 10)
    state_dist = db.query(
        Doctor.state,
        func.count(Doctor.npi).label('count')
    ).filter(Doctor.state.isnot(None))\
        .group_by(Doctor.state)\
        .order_by(func.count(Doctor.npi).desc())\
        .limit(10)\
        .all()
    
    return {
        "total_doctors": total_doctors,
        "total_monetary": float(total_monetary),
        "avg_monetary": float(avg_monetary),
        "avg_frequency": float(avg_frequency),
        "specialty_distribution": {s[0]: s[1] for s in specialty_dist if s[0]},
        "state_distribution": {s[0]: s[1] for s in state_dist if s[0]}
    }


@router.get("/specialties")
async def get_specialties(db: Session = Depends(get_db)):
    """Get list of all unique specialties."""
    specialties = db.query(Doctor.specialty)\
        .filter(Doctor.specialty.isnot(None))\
        .distinct()\
        .order_by(Doctor.specialty)\
        .limit(100)\
        .all()
    return {"specialties": [s[0] for s in specialties if s[0]]}


@router.get("/states")
async def get_states(db: Session = Depends(get_db)):
    """Get list of all unique states."""
    states = db.query(Doctor.state)\
        .filter(Doctor.state.isnot(None))\
        .distinct()\
        .order_by(Doctor.state)\
        .all()
    return {"states": [s[0] for s in states if s[0]]}


@router.get("/{npi}", response_model=DoctorDetailResponse)
async def get_doctor_detail(npi: str, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific doctor.
    Includes RFM values and recent payment history.
    """
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get recent payments (last 10)
    recent_payments = db.query(PaymentRecord)\
        .filter(PaymentRecord.npi == npi)\
        .order_by(PaymentRecord.payment_date.desc())\
        .limit(10)\
        .all()
    
    return {
        "doctor": doctor,
        "recent_payments": recent_payments
    }


@router.get("/{npi}/payments")
async def get_doctor_payments(
    npi: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated payment history for a doctor."""
    doctor = db.query(Doctor).filter(Doctor.npi == npi).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    query = db.query(PaymentRecord).filter(PaymentRecord.npi == npi)
    total = query.count()
    
    payments = query.order_by(PaymentRecord.payment_date.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return {
        "total": total,
        "items": payments
    }
