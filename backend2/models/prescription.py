# backend/models/prescription.py
"""Prescription and Drug models"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class DrugSchedule(str, Enum):
    """Drug schedule classification"""
    SCHEDULE_I = "schedule_i"      # High abuse potential, no medical use
    SCHEDULE_II = "schedule_ii"    # High abuse potential, medical use
    SCHEDULE_III = "schedule_iii"  # Moderate abuse potential
    SCHEDULE_IV = "schedule_iv"    # Low abuse potential
    SCHEDULE_V = "schedule_v"      # Lowest abuse potential
    OTC = "otc"                    # Over the counter
    UNSCHEDULED = "unscheduled"    # Not controlled


class DrugForm(str, Enum):
    """Drug form/type"""
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    CREAM = "cream"
    OINTMENT = "ointment"
    DROPS = "drops"
    INHALER = "inhaler"
    PATCH = "patch"
    SUPPOSITORY = "suppository"
    OTHER = "other"


class RouteOfAdministration(str, Enum):
    """How drug is administered"""
    ORAL = "oral"
    SUBLINGUAL = "sublingual"
    RECTAL = "rectal"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    NASAL = "nasal"
    OPHTHALMIC = "ophthalmic"
    OTIC = "otic"


class PrescriptionStatus(str, Enum):
    """Prescription status"""
    PENDING = "pending"
    ACTIVE = "active"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ON_HOLD = "on_hold"


class Drug(MongoBaseModel):
    """Drug collection model"""
    drug_id: str = Field(..., description="Unique drug identifier")
    generic_name: str = Field(..., max_length=200, description="Generic drug name")
    brand_name: Optional[str] = Field(None, max_length=200, description="Brand name")
    
    # Drug classification
    drug_class: str = Field(..., max_length=200, description="Therapeutic class")
    drug_schedule: DrugSchedule = Field(default=DrugSchedule.UNSCHEDULED)
    is_controlled: bool = Field(default=False, description="Whether controlled substance")
    
    # Drug form and strength
    form: DrugForm = Field(..., description="Drug form")
    strength: str = Field(..., max_length=100, description="Drug strength (e.g., '500mg')")
    strength_units: str = Field(..., max_length=50, description="Units of strength")
    
    # Administration
    route: RouteOfAdministration = Field(..., description="Route of administration")
    
    # Inventory and pricing
    in_stock: bool = Field(default=True, description="Whether currently in stock")
    quantity_in_stock: Optional[int] = Field(None, description="Current stock level")
    unit_price: Decimal = Field(..., description="Price per unit")
    
    # Insurance coverage
    is_covered_by_ohip: bool = Field(default=False, description="Covered by government insurance")
    requires_prior_auth: bool = Field(default=False, description="Requires insurance pre-approval")
    
    # Clinical information
    indications: List[str] = Field(default_factory=list, description="What drug treats")
    contraindications: List[str] = Field(default_factory=list, description="When not to use")
    side_effects: List[str] = Field(default_factory=list, description="Common side effects")
    interactions: List[str] = Field(default_factory=list, description="Drug interactions")
    
    # Warnings and precautions
    black_box_warning: Optional[str] = Field(None, description="FDA black box warning if any")
    pregnancy_category: Optional[str] = Field(None, description="Pregnancy safety category")
    requires_monitoring: bool = Field(default=False, description="Requires lab monitoring")
    monitoring_parameters: List[str] = Field(default_factory=list, description="What to monitor")
    
    # Additional information
    manufacturer: Optional[str] = Field(None, max_length=200)
    ndc_code: Optional[str] = Field(None, description="National Drug Code")
    din_number: Optional[str] = Field(None, description="Drug Identification Number (Canadian)")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "drug_id": "DRG001",
                "generic_name": "Amoxicillin",
                "brand_name": "Amoxil",
                "drug_class": "Antibiotic",
                "drug_schedule": "unscheduled",
                "form": "capsule",
                "strength": "500",
                "strength_units": "mg",
                "route": "oral",
                "unit_price": 0.50,
                "is_covered_by_ohip": True,
                "indications": ["Bacterial infections", "Pneumonia", "Bronchitis"],
                "side_effects": ["Nausea", "Diarrhea", "Rash"]
            }
        }


class Prescription(MongoBaseModel):
    """Prescription collection model"""
    prescription_id: str = Field(..., description="Unique prescription identifier")
    prescription_number: str = Field(..., description="Prescription number for pharmacy")
    visit_id: str = Field(..., description="Reference to Visit")
    patient_id: str = Field(..., description="Reference to Patient")
    drug_id: str = Field(..., description="Reference to Drug")
    prescribed_by: str = Field(..., description="Staff ID who prescribed")
    
    # Prescription details
    prescription_date: datetime = Field(default_factory=datetime.utcnow)
    status: PrescriptionStatus = Field(default=PrescriptionStatus.PENDING)
    
    # Dosage information
    dosage: str = Field(..., max_length=100, description="Dosage amount (e.g., '500mg')")
    frequency: str = Field(..., max_length=100, description="How often (e.g., 'twice daily')")
    route: RouteOfAdministration = Field(..., description="Route of administration")
    
    # Duration and quantity
    duration_days: Optional[int] = Field(None, description="Duration of treatment in days")
    quantity_prescribed: int = Field(..., description="Total quantity prescribed")
    quantity_dispensed: Optional[int] = Field(None, description="Quantity actually dispensed")
    refills_authorized: int = Field(default=0, description="Number of refills allowed")
    refills_remaining: Optional[int] = Field(None, description="Refills left")
    
    # Instructions
    instructions: str = Field(..., max_length=500, description="Patient instructions")
    pharmacy_notes: Optional[str] = Field(None, description="Notes for pharmacist")
    
    # Dates
    start_date: date = Field(default_factory=date.today, description="When to start medication")
    end_date: Optional[date] = Field(None, description="When to stop medication")
    expiry_date: date = Field(..., description="Prescription expiry date")
    
    # Dispensing information
    dispensed_by: Optional[str] = Field(None, description="Pharmacist who dispensed")
    dispensed_at: Optional[datetime] = Field(None, description="When dispensed")
    pharmacy_id: Optional[str] = Field(None, description="Pharmacy that filled prescription")
    
    # Substitution
    generic_substitution_allowed: bool = Field(default=True)
    brand_necessary: bool = Field(default=False, description="Brand medically necessary")
    substituted_drug_id: Optional[str] = Field(None, description="If substituted, what drug")
    
    # Special instructions
    take_with_food: Optional[bool] = Field(None)
    avoid_alcohol: Optional[bool] = Field(None)
    prn: bool = Field(default=False, description="Take as needed")
    prn_instructions: Optional[str] = Field(None, description="When to take if PRN")
    
    # Label information (for printing)
    label_instructions: Optional[str] = Field(None, description="Instructions for label")
    warning_labels: List[str] = Field(default_factory=list, description="Warning labels to print")
    
    # Billing
    is_billed: bool = Field(default=False)
    invoice_line_id: Optional[str] = Field(None, description="Reference to InvoiceLine")
    
    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if 'prescription_date' in values:
            # Prescriptions typically expire after 1 year
            min_expiry = values['prescription_date'].date()
            if v <= min_expiry:
                raise ValueError('Expiry date must be after prescription date')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('refills_remaining', always=True)
    def set_initial_refills(cls, v, values):
        if v is None and 'refills_authorized' in values:
            return values['refills_authorized']
        return v
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "prescription_id": "RX001",
                "prescription_number": "RX2024-0001",
                "visit_id": "VIS001",
                "patient_id": "PAT001",
                "drug_id": "DRG001",
                "prescribed_by": "STF001",
                "prescription_date": "2024-02-01T10:00:00",
                "dosage": "500mg",
                "frequency": "twice daily",
                "route": "oral",
                "duration_days": 10,
                "quantity_prescribed": 20,
                "refills_authorized": 2,
                "instructions": "Take with food. Complete entire course.",
                "start_date": "2024-02-01",
                "expiry_date": "2025-02-01"
            }
        }


# Request models for API
class PrescriptionCreateRequest(BaseModel):
    """Request model for creating a prescription"""
    visit_id: str
    drug_id: str
    dosage: str
    frequency: str
    route: RouteOfAdministration
    duration_days: Optional[int] = None
    quantity_prescribed: int
    refills_authorized: int = 0
    instructions: str
    pharmacy_notes: Optional[str] = None
    generic_substitution_allowed: bool = True
    take_with_food: Optional[bool] = None
    avoid_alcohol: Optional[bool] = None
    prn: bool = False
    prn_instructions: Optional[str] = None


class PrescriptionFillRequest(BaseModel):
    """Request model for filling a prescription"""
    prescription_id: str
    quantity_dispensed: int
    dispensed_by: str
    pharmacy_id: Optional[str] = None
    substituted_drug_id: Optional[str] = None


class PrescriptionRefillRequest(BaseModel):
    """Request model for refilling a prescription"""
    prescription_id: str
    quantity_dispensed: int
    dispensed_by: str


class PrescriptionLabelData(BaseModel):
    """Data structure for prescription label printing"""
    patient_name: str
    patient_address: str
    patient_phone: str
    prescription_number: str
    drug_name: str
    strength: str
    quantity: int
    instructions: str
    prescriber_name: str
    prescriber_license: str
    date_filled: date
    expiry_date: date
    refills_remaining: int
    warning_labels: List[str]
    pharmacy_name: str
    pharmacy_address: str
    pharmacy_phone: str


class DrugSearchRequest(BaseModel):
    """Request model for searching drugs"""
    search_term: Optional[str] = Field(None, description="Search in generic/brand name")
    drug_class: Optional[str] = None
    form: Optional[DrugForm] = None
    in_stock: Optional[bool] = True