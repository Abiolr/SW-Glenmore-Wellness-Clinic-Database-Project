# backend/models/lab.py
"""LabTestOrder model"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class TestStatus(str, Enum):
    """Lab test status options"""
    ORDERED = "ordered"
    SCHEDULED = "scheduled"
    SPECIMEN_COLLECTED = "specimen_collected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PENDING_REVIEW = "pending_review"


class TestPriority(str, Enum):
    """Test priority levels"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"  # Immediate


class SpecimenType(str, Enum):
    """Types of specimens"""
    BLOOD = "blood"
    URINE = "urine"
    STOOL = "stool"
    SPUTUM = "sputum"
    SWAB = "swab"
    TISSUE = "tissue"
    FLUID = "fluid"
    OTHER = "other"


class TestCategory(str, Enum):
    """Lab test categories"""
    HEMATOLOGY = "hematology"
    CHEMISTRY = "chemistry"
    MICROBIOLOGY = "microbiology"
    IMMUNOLOGY = "immunology"
    PATHOLOGY = "pathology"
    GENETICS = "genetics"
    TOXICOLOGY = "toxicology"
    URINALYSIS = "urinalysis"
    OTHER = "other"


class LabTestOrder(MongoBaseModel):
    """LabTestOrder collection model"""
    lab_test_id: str = Field(..., description="Unique lab test identifier")
    order_number: str = Field(..., description="Lab order number")
    patient_id: str = Field(..., description="Reference to Patient")
    visit_id: Optional[str] = Field(None, description="Reference to Visit if applicable")
    
    # Test information
    test_name: str = Field(..., max_length=200, description="Name of the test")
    test_code: Optional[str] = Field(None, max_length=50, description="Lab test code")
    test_category: TestCategory = Field(..., description="Category of test")
    test_description: Optional[str] = Field(None, max_length=500)
    
    # Ordering information
    ordered_by: str = Field(..., description="Staff ID who ordered test")
    ordered_at: datetime = Field(default_factory=datetime.utcnow)
    priority: TestPriority = Field(default=TestPriority.ROUTINE)
    status: TestStatus = Field(default=TestStatus.ORDERED)
    
    # Clinical information
    clinical_notes: Optional[str] = Field(None, description="Clinical notes for lab")
    diagnosis_codes: List[str] = Field(default_factory=list, description="Related diagnosis codes")
    symptoms: List[str] = Field(default_factory=list, description="Patient symptoms")
    fasting_required: bool = Field(default=False)
    special_instructions: Optional[str] = Field(None, description="Special prep instructions")
    
    # Specimen information
    specimen_type: Optional[SpecimenType] = None
    specimen_collected_by: Optional[str] = Field(None, description="Staff ID who collected")
    specimen_collected_at: Optional[datetime] = None
    specimen_id: Optional[str] = Field(None, description="Specimen tracking ID")
    collection_notes: Optional[str] = Field(None, description="Collection notes")
    
    # Scheduling
    scheduled_date: Optional[date] = Field(None, description="When test is scheduled")
    scheduled_time: Optional[datetime] = Field(None, description="Scheduled time slot")
    
    # Performance
    performed_by: Optional[str] = Field(None, description="Staff/Lab technician ID")
    performed_at: Optional[datetime] = None
    lab_location: Optional[str] = Field(None, description="Internal or external lab")
    external_lab_name: Optional[str] = Field(None, description="If external, lab name")
    
    # Results
    result: Optional[Dict[str, Any]] = Field(None, description="Test results")
    result_date: Optional[datetime] = None
    result_status: Optional[str] = Field(None, description="normal, abnormal, critical")
    reference_range: Optional[str] = Field(None, description="Normal reference range")
    abnormal_flags: List[str] = Field(default_factory=list, description="Abnormal result flags")
    critical_values: List[str] = Field(default_factory=list, description="Critical values requiring immediate attention")
    
    # Result interpretation
    interpretation: Optional[str] = Field(None, description="Result interpretation")
    reviewed_by: Optional[str] = Field(None, description="Staff ID who reviewed results")
    reviewed_at: Optional[datetime] = None
    
    # Billing
    is_billed: bool = Field(default=False)
    invoice_line_id: Optional[str] = Field(None, description="Reference to InvoiceLine")
    test_fee: Optional[Decimal] = Field(None, description="Cost of test")
    is_covered_by_insurance: bool = Field(default=False)
    
    # Notifications
    patient_notified: bool = Field(default=False)
    patient_notified_at: Optional[datetime] = None
    provider_notified: bool = Field(default=False)
    provider_notified_at: Optional[datetime] = None
    requires_follow_up: bool = Field(default=False)
    follow_up_notes: Optional[str] = None
    
    # Cancellation
    cancelled_by: Optional[str] = Field(None, description="Staff ID who cancelled")
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    @validator('result_status')
    def validate_result_status(cls, v):
        if v and v not in ['normal', 'abnormal', 'critical', 'inconclusive']:
            raise ValueError('Invalid result status')
        return v
    
    @validator('specimen_collected_at')
    def validate_collection_time(cls, v, values):
        if v and 'ordered_at' in values and v < values['ordered_at']:
            raise ValueError('Specimen cannot be collected before test is ordered')
        return v
    
    @property
    def turnaround_time_hours(self) -> Optional[float]:
        """Calculate turnaround time in hours"""
        if self.ordered_at and self.result_date:
            delta = self.result_date - self.ordered_at
            return delta.total_seconds() / 3600
        return None
    
    @property
    def is_critical(self) -> bool:
        """Check if results contain critical values"""
        return len(self.critical_values) > 0
    
    @property
    def is_abnormal(self) -> bool:
        """Check if results are abnormal"""
        return self.result_status == 'abnormal' or self.result_status == 'critical'
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "lab_test_id": "LAB001",
                "order_number": "LAB2024-0001",
                "patient_id": "PAT001",
                "visit_id": "VIS001",
                "test_name": "Complete Blood Count",
                "test_code": "CBC",
                "test_category": "hematology",
                "ordered_by": "STF001",
                "ordered_at": "2024-02-01T09:30:00",
                "priority": "routine",
                "status": "ordered",
                "specimen_type": "blood",
                "fasting_required": False
            }
        }


# Request models for API
class LabTestOrderCreateRequest(BaseModel):
    """Request model for ordering a lab test"""
    patient_id: str
    visit_id: Optional[str] = None
    test_name: str
    test_code: Optional[str] = None
    test_category: TestCategory
    priority: TestPriority = TestPriority.ROUTINE
    clinical_notes: Optional[str] = None
    diagnosis_codes: Optional[List[str]] = None
    fasting_required: bool = False
    special_instructions: Optional[str] = None
    scheduled_date: Optional[date] = None


class SpecimenCollectionRequest(BaseModel):
    """Request model for recording specimen collection"""
    lab_test_id: str
    specimen_type: SpecimenType
    specimen_id: str
    collection_notes: Optional[str] = None


class LabResultEntryRequest(BaseModel):
    """Request model for entering lab results"""
    lab_test_id: str
    result: Dict[str, Any]
    result_status: str  # normal, abnormal, critical
    reference_range: Optional[str] = None
    abnormal_flags: Optional[List[str]] = None
    critical_values: Optional[List[str]] = None
    interpretation: Optional[str] = None


class LabTestSearchRequest(BaseModel):
    """Request model for searching lab tests"""
    patient_id: Optional[str] = None
    visit_id: Optional[str] = None
    status: Optional[TestStatus] = None
    priority: Optional[TestPriority] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    pending_results: Optional[bool] = None
    abnormal_only: Optional[bool] = False


class DailyLabLogRequest(BaseModel):
    """Request model for daily lab log report"""
    log_date: date = Field(default_factory=date.today)
    include_external: bool = True
    group_by_category: bool = True
