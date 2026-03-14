# Developer Guide: Pharma Market Intelligent Analysis System

## 1. Core Data Field Analysis

Based on the `data_report.txt` and `data_sample.csv` from the CMS Open Payments dataset, the following fields have been selected as critical for **Doctor Profiling** and **RFM (Recency, Frequency, Monetary) Clustering Analysis**.

| Original Field Name (CSV Header) | Recommended Backend Field (Snake Case) | Data Type (Python/SQL) | Business Meaning | Selection Reason |
| :--- | :--- | :--- | :--- | :--- |
| `Covered_Recipient_NPI` | `npi` | `str` / `VARCHAR(10)` | National Provider Identifier (Unique Doctor ID). | **Primary Key**. Essential for aggregating payments to a specific doctor. |
| `Covered_Recipient_First_Name` | `first_name` | `str` / `VARCHAR(50)` | Doctor's first name. | **Profile**. Basic identification for UI display. |
| `Covered_Recipient_Last_Name` | `last_name` | `str` / `VARCHAR(50)` | Doctor's last name. | **Profile**. Basic identification for UI display. |
| `Covered_Recipient_Specialty_1` | `specialty` | `str` / `VARCHAR(100)` | Primary medical specialty (e.g., Cardiology). | **Profile & Clustering**. Critical for grouping doctors by domain (e.g., comparing Oncologists vs. Dentists). |
| `Recipient_City` | `city` | `str` / `VARCHAR(50)` | Practice city. | **Profile**. Geographic dimension for regional analysis. |
| `Recipient_State` | `state` | `str` / `VARCHAR(2)` | Practice state (e.g., CA, NY). | **Profile**. Geographic dimension for regional analysis. |
| `Total_Amount_of_Payment_USDollars` | `amount` | `float` / `DECIMAL(12,2)` | Transaction amount in USD. | **Monetary (M)**. The core metric for "Value" in RFM. Sum of this = M Score. |
| `Date_of_Payment` | `payment_date` | `date` / `DATE` | Date when the payment was made. | **Recency (R)**. Used to calculate how recently a doctor received payment (Max Date). |
| `Number_of_Payments_Included_in_Total_Amount` | `payment_count` | `int` / `INTEGER` | Number of payments in this transaction line. | **Frequency (F)**. Usually 1, but if aggregated, needs to be summed to get true frequency. |
| `Nature_of_Payment_or_Transfer_of_Value` | `nature_of_payment` | `str` / `VARCHAR(100)` | Reason for payment (e.g., Consulting, Food, Travel). | **Behavior Feature**. Distinguishes "Academic/KOL" doctors (Consulting/Speaking) from others. |
| `Submitting_Applicable_Manufacturer_or_Applicable_GPO_Name` | `payer_name` | `str` / `VARCHAR(100)` | The Pharma/Device company paying. | **Relationship**. Shows brand loyalty or breadth of industry relationships. |

---

## 2. Backend Pydantic Model Design

The following Pydantic models should be implemented in `backend/app/schemas.py` to support data ingestion and validation.

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

class PaymentRecordBase(BaseModel):
    """
    Base schema for a single Open Payments transaction record.
    """
    npi: str = Field(
        ..., 
        description="10-digit National Provider Identifier (NPI)", 
        min_length=10, 
        max_length=10
    )
    first_name: Optional[str] = Field(None, description="Doctor's first name")
    last_name: Optional[str] = Field(None, description="Doctor's last name")
    specialty: Optional[str] = Field(None, description="Primary medical specialty")
    city: Optional[str] = Field(None, description="City of practice")
    state: Optional[str] = Field(None, description="State abbreviation (e.g. CA)", max_length=2)
    
    amount: float = Field(..., description="Transaction amount in USD")
    payment_date: date = Field(..., description="Date of the payment")
    payment_count: int = Field(1, description="Number of payments included in this record")
    nature_of_payment: Optional[str] = Field(None, description="Nature of payment (e.g., Food and Beverage)")
    payer_name: Optional[str] = Field(None, description="Name of the entity making the payment")

    @field_validator('amount')
    def amount_must_be_positive_or_zero(cls, v):
        if v < 0:
            raise ValueError('Amount must be non-negative')
        return v

    @field_validator('npi')
    def npi_must_be_numeric(cls, v):
        if not v.isdigit():
            raise ValueError('NPI must contain only digits')
        return v

class PaymentRecordCreate(PaymentRecordBase):
    """Schema for creating a new record (input)"""
    pass

class PaymentRecord(PaymentRecordBase):
    """Schema for reading a record (output)"""
    id: int

    class Config:
        from_attributes = True
```

---

## 3. Core API Specification

### Interface A: Execute Clustering Analysis

* **Method/URL**: `POST /api/v1/analysis/run-clustering`
* **Summary**: Triggers the K-Means algorithm to group doctors based on RFM features.
* **Description**: This asynchronous endpoint reads aggregated doctor data, computes R/F/M scores, standardizes them (Scaler), and applies K-Means clustering.

#### Request Body (JSON)

```json
{
  "k": 4,
  "features": ["monetary", "frequency", "recency"],
  "algorithm": "kmeans",
  "scaling": "standard",
  "task_name": "Q4 2024 High Value Doctor Analysis"
}
```

* `k` (int, optional): Number of clusters. Default determined by Elbow Method if null.
* `features` (list[str]): Fields to use for clustering.
* `task_name`: Label for this analysis execution.

#### Response (JSON)

```json
{
  "project_id": "proj_12345",
  "status": "completed",
  "clusters_summary": [
    {
      "cluster_id": 0,
      "label": "High Value KOLs",
      "count": 150,
      "percentage": "15%",
      "avg_monetary": 50000.00,
      "avg_frequency": 25.5
    },
    {
      "cluster_id": 1,
      "label": "Low Engagement",
      "count": 850,
      "percentage": "85%",
      "avg_monetary": 120.00,
      "avg_frequency": 1.2
    }
  ],
  "visualization_data": {
      "scatter_plot": [ ... ] 
  }
}
```

### Interface B: AI Strategy Chat

* **Method/URL**: `POST /api/v1/chat`
* **Summary**: Interactive AI agent to interpret clustering results and suggest marketing strategies.
* **Description**: Uses an LLM (via Dify or direct API) to answer questions about specific doctor clusters.

#### Request Body (JSON)

```json
{
  "query": "How should we target the 'High Value KOLs' group for the new drug launch?",
  "cluster_id": 0,
  "context_data": {
     "avg_monetary": 50000.00,
     "top_specialties": ["Cardiology", "Oncology"],
     "preferred_payment_nature": ["Consulting Fee", "Travel"]
  }
}
```

#### Response (JSON)

```json
{
  "answer": "For the 'High Value KOLs' group, specifically Cardiologists and Oncologists who prefer Consulting Fees, your strategy should focus on Academic Partnership programs rather than simple sales visits. \n\n**Strategy:**\n1. Invite them to advisory boards.\n2. Sponsor speaking engagements at key conferences.\n3. Avoid small-value interactions (food/beverage) as they are less impactful.",
  "reasoning": "Based on the high monetary value and preference for 'Consulting', these are Opinion Leaders, not standard prescribers.",
  "suggested_actions": [
      "Create Advisory Board Invitation",
      "Schedule Medical Science Liaison (MSL) visit"
  ]
}
```
