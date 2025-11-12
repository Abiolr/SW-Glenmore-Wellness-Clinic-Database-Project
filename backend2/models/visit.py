# backend/models/visit.py
"""Visit, VisitDiagnosis, VisitProcedure, Diagnosis, and Procedure models"""

from typing import Optional, List, Dict
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class VisitType(str, Enum):
    """Visit type options"""
    REGULAR = "regular"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"
    CHECKUP = "checkup"
    IMMUNIZATION = "immunization"
    PRENATAL = "prenatal"
    POSTNATAL = "postnatal"
    DELIVERY = "delivery"
    LAB_ONLY = "lab_only"


class VisitStatus(str, Enum):
    """Visit status options"""
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    AWAITING_LAB = "awaiting_lab"
    AWAITING_PRESCRIPTION = "awaiting_prescription"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class DiagnosisType(str, Enum):
    """Diagnosis type options"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ADMITTING = "admitting"
    DIFFERENTIAL = "differential"
    WORKING = "working"
    NURSING = "nursing"


class Visit(MongoBaseModel):
    """Visit collection model"""
    visit_id: str = Field(..., description="Unique visit identifier")
    patient_id: str = Field(..., description="Reference to Patient")
    staff_id: str = Field(..., description="Reference to primary Staff (practitioner)")
    appointment_id: Optional[str] = Field(None, description="Reference to Appointment if scheduled")
    
    # Visit timing
    visit_date: date = Field(..., description="Date of visit")
    check_in_time: datetime = Field(..., description="When patient checked in")
    start_time: Optional[datetime] = Field(None, description="When visit actually started")
    end_time: Optional[datetime] = Field(None, description="When visit ended")
    
    # Visit details
    visit_type: VisitType = Field(default=VisitType.REGULAR)
    status: VisitStatus = Field(default=VisitStatus.CHECKED_IN)
    chief_complaint: str = Field(..., max_length=500, description="Primary reason for visit")
    presenting_symptoms: List[str] = Field(default_factory=list, description="List of symptoms")
    
    # Vital signs
    vitals: Dict = Field(default_factory=dict, description="Vital signs measurements")
    # Format: {"temperature": 98.6, "blood_pressure": "120/80", "pulse": 72, "weight": 70}
    
    # Clinical notes
    history_of_present_illness: Optional[str] = Field(None, description="HPI notes")
    review_of_systems: Optional[str] = Field(None, description="ROS notes")
    physical_exam_findings: Optional[str] = Field(None, description="Physical examination notes")
    assessment_plan: Optional[str] = Field(None, description="Assessment and plan")
    
    # Additional providers
    additional_staff_ids: List[str] = Field(default_factory=list, description="Other staff involved")
    nurse_id: Optional[str] = Field(None, description="Attending nurse")
    
    # Referrals and follow-up
    referrals: List[dict] = Field(default_factory=list, description="Referrals made")
    # Format: [{"specialty": "cardiology", "provider": "Dr. Smith", "reason": "..."}]
    follow_up_required: bool = Field(default=False)
    follow_up_instructions: Optional[str] = None
    
    # Billing
    is_billed: bool = Field(default=False, description="Whether visit has been billed")
    billed_at: Optional[datetime] = None
    invoice_id: Optional[str] = Field(None, description="Reference to Invoice")
    
    @validator('end_time')
    def validate_end_after_start(cls, v, values):
        if 'start_time' in values and values['start_time'] and v:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate visit duration in minutes"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds() / 60)
        return None
    
    class Config:
        schema_extra = {
            "example": {
                "visit_id": "VIS001",
                "patient_id": "PAT001",
                "staff_id": "STF001",
                "appointment_id": "APT001",
                "visit_date": "2024-02-01",
                "check_in_time": "2024-02-01T09:00:00",
                "start_time": "2024-02-01T09:10:00",
                "visit_type": "regular",
                "status": "in_progress",
                "chief_complaint": "Persistent cough for 2 weeks",
                "vitals": {
                    "temperature": 98.6,
                    "blood_pressure": "120/80",
                    "pulse": 72,
                    "respiratory_rate": 16
                }
            }
        }


class Diagnosis(MongoBaseModel):
    """Diagnosis collection model"""
    diagnosis_id: str = Field(..., description="Unique diagnosis identifier")
    code: str = Field(..., description="ICD-10 or other coding system code")
    description: str = Field(..., max_length=500)
    category: Optional[str] = Field(None, max_length=200, description="Diagnosis category")
    is_chronic: bool = Field(default=False, description="Whether this is a chronic condition")
    is_infectious: bool = Field(default=False, description="Whether this is infectious")
    requires_followup: bool = Field(default=False, description="Whether followup is typically required")
    
    class Config:
        schema_extra = {
            "example": {
                "diagnosis_id": "DIA001",
                "code": "J20.9",
                "description": "Acute bronchitis, unspecified",
                "category": "Respiratory",
                "is_chronic": False,
                "is_infectious": True,
                "requires_followup": True
            }
        }


class Procedure(MongoBaseModel):
    """Procedure collection model"""
    procedure_id: str = Field(..., description="Unique procedure identifier")
    code: str = Field(..., description="CPT or other procedure code")
    description: str = Field(..., max_length=500)
    category: Optional[str] = Field(None, max_length=200, description="Procedure category")
    typical_duration_minutes: int = Field(default=10, description="Typical duration")
    requires_consent: bool = Field(default=False, description="Whether consent form required")
    
    # Billing information
    standard_fee: Decimal = Field(..., description="Standard fee for procedure")
    is_covered_by_ohip: bool = Field(default=False, description="Whether covered by government insurance")
    
    # Requirements
    requires_fasting: bool = Field(default=False)
    requires_preparation: bool = Field(default=False)
    preparation_instructions: Optional[str] = Field(None, description="Preparation instructions")
    
    class Config:
        schema_extra = {
            "example": {
                "procedure_id": "PRO001",
                "code": "99213",
                "description": "Office visit, established patient, 15 minutes",
                "category": "Evaluation and Management",
                "typical_duration_minutes": 15,
                "standard_fee": 150.00,
                "is_covered_by_ohip": True
            }
        }


class VisitDiagnosis(MongoBaseModel):
    """VisitDiagnosis junction collection model"""
    visit_id: str = Field(..., description="Reference to Visit")
    diagnosis_id: str = Field(..., description="Reference to Diagnosis")
    diagnosis_type: DiagnosisType = Field(default=DiagnosisType.PRIMARY)
    diagnosed_by: str = Field(..., description="Staff ID who made diagnosis")
    diagnosed_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(None, description="Additional notes about this diagnosis")
    severity: Optional[str] = Field(None, description="mild, moderate, severe")
    
    class Config:
        schema_extra = {
            "example": {
                "visit_id": "VIS001",
                "diagnosis_id": "DIA001",
                "diagnosis_type": "primary",
                "diagnosed_by": "STF001",
                "diagnosed_at": "2024-02-01T09:30:00",
                "severity": "moderate"
            }
        }


class VisitProcedure(MongoBaseModel):
    """VisitProcedure junction collection model"""
    visit_id: str = Field(..., description="Reference to Visit")
    procedure_id: str = Field(..., description="Reference to Procedure")
    performed_by: str = Field(..., description="Staff ID who performed procedure")
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Procedure details
    quantity: int = Field(default=1, description="Number of times procedure performed")
    duration_minutes: Optional[int] = Field(None, description="Actual duration")
    
    # Billing
    fee: Decimal = Field(..., description="Fee charged for this procedure")
    discount_percentage: Optional[Decimal] = Field(None, description="Discount applied")
    final_fee: Optional[Decimal] = Field(None, description="Final fee after discount")
    
    # Notes and outcomes
    notes: Optional[str] = Field(None, description="Procedure notes")
    complications: Optional[str] = Field(None, description="Any complications")
    outcome: Optional[str] = Field(None, description="Procedure outcome")
    
    @validator('final_fee', always=True)
    def calculate_final_fee(cls, v, values):
        if v is None:
            fee = values.get('fee')
            discount = values.get('discount_percentage', 0)
            if fee and discount:
                return fee * (1 - discount / 100)
            return fee
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "visit_id": "VIS001",
                "procedure_id": "PRO001",
                "performed_by": "STF001",
                "performed_at": "2024-02-01T09:20:00",
                "quantity": 1,
                "duration_minutes": 15,
                "fee": 150.00,
                "final_fee": 150.00
            }
        }


# Request models for API
class VisitCreateRequest(BaseModel):
    """Request model for creating a visit"""
    patient_id: str
    staff_id: str
    appointment_id: Optional[str] = None
    visit_type: VisitType = VisitType.REGULAR
    chief_complaint: str
    presenting_symptoms: Optional[List[str]] = None


class VisitUpdateRequest(BaseModel):
    """Request model for updating a visit"""
    status: Optional[VisitStatus] = None
    vitals: Optional[Dict] = None
    history_of_present_illness: Optional[str] = None
    review_of_systems: Optional[str] = None
    physical_exam_findings: Optional[str] = None
    assessment_plan: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_instructions: Optional[str] = None


class AddDiagnosisRequest(BaseModel):
    """Request model for adding diagnosis to visit"""
    diagnosis_id: str
    diagnosis_type: DiagnosisType = DiagnosisType.PRIMARY
    notes: Optional[str] = None
    severity: Optional[str] = None


class AddProcedureRequest(BaseModel):
    """Request model for adding procedure to visit"""
    procedure_id: str
    quantity: int = 1
    fee: Decimal
    notes: Optional[str] = None