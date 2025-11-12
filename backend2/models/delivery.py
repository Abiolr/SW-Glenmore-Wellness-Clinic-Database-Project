# backend/models/delivery.py
"""Delivery model for birthing room operations"""

from typing import Optional, List, Dict
from datetime import datetime, date, time
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class DeliveryType(str, Enum):
    """Types of delivery"""
    VAGINAL_SPONTANEOUS = "vaginal_spontaneous"
    VAGINAL_ASSISTED = "vaginal_assisted"
    CESAREAN_PLANNED = "cesarean_planned"
    CESAREAN_EMERGENCY = "cesarean_emergency"
    VBAC = "vbac"  # Vaginal birth after cesarean
    BREECH = "breech"
    MULTIPLE = "multiple"  # Twins, triplets, etc.


class DeliveryComplication(str, Enum):
    """Possible delivery complications"""
    NONE = "none"
    PROLONGED_LABOR = "prolonged_labor"
    FETAL_DISTRESS = "fetal_distress"
    HEMORRHAGE = "hemorrhage"
    PLACENTA_PREVIA = "placenta_previa"
    PLACENTAL_ABRUPTION = "placental_abruption"
    CORD_PROLAPSE = "cord_prolapse"
    SHOULDER_DYSTOCIA = "shoulder_dystocia"
    PREECLAMPSIA = "preeclampsia"
    OTHER = "other"


class BabyGender(str, Enum):
    """Baby gender options"""
    MALE = "male"
    FEMALE = "female"
    UNDETERMINED = "undetermined"


class Delivery(MongoBaseModel):
    """Delivery collection model"""
    delivery_id: str = Field(..., description="Unique delivery identifier")
    patient_id: str = Field(..., description="Reference to Patient (mother)")
    visit_id: str = Field(..., description="Reference to Visit")
    
    # Delivery team
    midwife_id: str = Field(..., description="Primary midwife")
    physician_id: Optional[str] = Field(None, description="Physician if involved")
    nurse_ids: List[str] = Field(default_factory=list, description="Assisting nurses")
    
    # Admission information
    admitted_at: datetime = Field(..., description="When admitted to birthing room")
    labor_start_time: Optional[datetime] = Field(None, description="When labor started")
    membrane_rupture_time: Optional[datetime] = Field(None, description="When water broke")
    
    # Delivery information
    delivery_datetime: datetime = Field(..., description="Actual delivery time")
    delivery_type: DeliveryType = Field(..., description="Type of delivery")
    delivery_room: str = Field(..., max_length=50, description="Room number/name")
    
    # Labor details
    labor_duration_hours: Optional[float] = Field(None, description="Total labor duration")
    epidural_given: bool = Field(default=False)
    epidural_time: Optional[datetime] = None
    pain_management: List[str] = Field(default_factory=list, description="Pain management methods")
    
    # Mother's condition
    mother_vitals_pre: Dict = Field(default_factory=dict, description="Vitals before delivery")
    mother_vitals_post: Dict = Field(default_factory=dict, description="Vitals after delivery")
    blood_loss_ml: Optional[int] = Field(None, description="Estimated blood loss")
    complications: List[DeliveryComplication] = Field(default_factory=list)
    complication_notes: Optional[str] = Field(None, max_length=1000)
    
    # Baby information
    baby_gender: BabyGender = Field(...)
    baby_weight_grams: int = Field(..., description="Baby weight in grams")
    baby_length_cm: Optional[float] = Field(None, description="Baby length in cm")
    apgar_1_min: Optional[int] = Field(None, ge=0, le=10, description="APGAR at 1 minute")
    apgar_5_min: Optional[int] = Field(None, ge=0, le=10, description="APGAR at 5 minutes")
    apgar_10_min: Optional[int] = Field(None, ge=0, le=10, description="APGAR at 10 minutes if needed")
    
    # Multiple births
    is_multiple_birth: bool = Field(default=False)
    birth_order: Optional[int] = Field(None, description="Order in multiple birth (1st, 2nd, etc.)")
    total_births: Optional[int] = Field(None, description="Total number in multiple birth")
    
    # Baby condition
    baby_vitals: Dict = Field(default_factory=dict, description="Baby's initial vitals")
    baby_complications: List[str] = Field(default_factory=list, description="Baby complications")
    nicu_transfer: bool = Field(default=False, description="Whether baby transferred to NICU")
    nicu_transfer_time: Optional[datetime] = None
    nicu_transfer_reason: Optional[str] = None
    
    # Placenta and cord
    placenta_delivered_time: Optional[datetime] = None
    placenta_complete: Optional[bool] = Field(None, description="Whether placenta delivered complete")
    cord_blood_collected: bool = Field(default=False)
    cord_complications: Optional[str] = Field(None, description="Cord around neck, etc.")
    
    # Post-delivery
    mother_recovery_start: Optional[datetime] = None
    skin_to_skin_time: Optional[datetime] = Field(None, description="When skin-to-skin started")
    first_feeding_time: Optional[datetime] = Field(None, description="First breastfeeding")
    
    # Documentation
    notes: Optional[str] = Field(None, description="Delivery notes")
    birth_certificate_filed: bool = Field(default=False)
    birth_certificate_number: Optional[str] = None
    
    # Discharge
    mother_discharged_at: Optional[datetime] = None
    baby_discharged_at: Optional[datetime] = None
    discharge_instructions: Optional[str] = None
    follow_up_scheduled: bool = Field(default=False)
    
    @validator('apgar_1_min', 'apgar_5_min', 'apgar_10_min')
    def validate_apgar(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('APGAR score must be between 0 and 10')
        return v
    
    @validator('baby_weight_grams')
    def validate_weight(cls, v):
        # Typical range: 500g (very premature) to 6000g (large baby)
        if v < 300 or v > 7000:
            raise ValueError('Baby weight seems incorrect, please verify')
        return v
    
    @validator('labor_duration_hours', always=True)
    def calculate_labor_duration(cls, v, values):
        if v is None and 'labor_start_time' in values and 'delivery_datetime' in values:
            if values['labor_start_time'] and values['delivery_datetime']:
                delta = values['delivery_datetime'] - values['labor_start_time']
                return delta.total_seconds() / 3600
        return v
    
    @property
    def baby_weight_lbs(self) -> float:
        """Convert baby weight to pounds"""
        return round(self.baby_weight_grams / 453.592, 2)
    
    @property
    def is_high_risk(self) -> bool:
        """Determine if this was a high-risk delivery"""
        high_risk_indicators = [
            self.delivery_type in [DeliveryType.CESAREAN_EMERGENCY, DeliveryType.BREECH],
            len(self.complications) > 0 and DeliveryComplication.NONE not in self.complications,
            self.nicu_transfer,
            self.apgar_1_min and self.apgar_1_min < 7,
            self.baby_weight_grams < 2500,  # Low birth weight
            self.is_multiple_birth
        ]
        return any(high_risk_indicators)
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "delivery_id": "DEL001",
                "patient_id": "PAT001",
                "visit_id": "VIS001",
                "midwife_id": "STF004",
                "admitted_at": "2024-02-01T02:00:00",
                "delivery_datetime": "2024-02-01T08:30:00",
                "delivery_type": "vaginal_spontaneous",
                "delivery_room": "Birthing Suite 1",
                "baby_gender": "female",
                "baby_weight_grams": 3200,
                "baby_length_cm": 50,
                "apgar_1_min": 8,
                "apgar_5_min": 9,
                "complications": ["none"]
            }
        }


# Request models for API
class DeliveryAdmissionRequest(BaseModel):
    """Request model for admitting patient to birthing room"""
    patient_id: str
    visit_id: str
    midwife_id: str
    delivery_room: str
    labor_start_time: Optional[datetime] = None
    membrane_rupture_time: Optional[datetime] = None
    mother_vitals: Dict


class DeliveryRecordRequest(BaseModel):
    """Request model for recording delivery"""
    delivery_id: str
    delivery_type: DeliveryType
    baby_gender: BabyGender
    baby_weight_grams: int
    baby_length_cm: Optional[float] = None
    apgar_1_min: Optional[int] = None
    apgar_5_min: Optional[int] = None
    complications: List[DeliveryComplication] = Field(default_factory=list)
    complication_notes: Optional[str] = None
    blood_loss_ml: Optional[int] = None


class BabyAssessmentRequest(BaseModel):
    """Request model for baby assessment after delivery"""
    delivery_id: str
    baby_vitals: Dict
    apgar_10_min: Optional[int] = None
    baby_complications: Optional[List[str]] = None
    nicu_transfer: bool = False
    nicu_transfer_reason: Optional[str] = None


class DeliveryDischargeRequest(BaseModel):
    """Request model for discharge after delivery"""
    delivery_id: str
    mother_discharge: bool = True
    baby_discharge: bool = True
    discharge_instructions: str
    follow_up_scheduled: bool


class DailyDeliveryLogRequest(BaseModel):
    """Request model for daily delivery log report"""
    log_date: date = Field(default_factory=date.today)
    include_complications: bool = True
    include_nicu_transfers: bool = True
