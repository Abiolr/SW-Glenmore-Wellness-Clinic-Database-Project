# backend/models/patient.py
"""Patient model"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
from .base import MongoBaseModel


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class BloodType(str, Enum):
    """Blood type options"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"


class MaritalStatus(str, Enum):
    """Marital status options"""
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"


class Patient(MongoBaseModel):
    """Patient collection model"""
    patient_id: str = Field(..., description="Unique patient identifier")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: date = Field(..., description="Patient's date of birth")
    gender: Gender = Field(..., description="Patient's gender")
    phone: str = Field(..., description="Primary phone number")
    alternate_phone: Optional[str] = Field(None, description="Alternate phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")
    address: str = Field(..., max_length=500)
    city: str = Field(..., max_length=100)
    province: str = Field(..., max_length=50)
    postal_code: str = Field(..., regex="^[A-Z]\\d[A-Z] \\d[A-Z]\\d$", description="Canadian postal code")
    
    # Medical information
    health_card_number: Optional[str] = Field(None, description="Government health card number")
    blood_type: Optional[BloodType] = None
    allergies: List[str] = Field(default_factory=list, description="List of known allergies")
    chronic_conditions: List[str] = Field(default_factory=list, description="List of chronic conditions")
    current_medications: List[str] = Field(default_factory=list, description="List of current medications")
    
    # Insurance information
    insurance_provider: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_group_number: Optional[str] = Field(None, max_length=100)
    
    # Emergency contact
    emergency_contact_name: str = Field(..., max_length=200)
    emergency_contact_phone: str = Field(...)
    emergency_contact_relationship: str = Field(..., max_length=100)
    
    # Additional information
    marital_status: Optional[MaritalStatus] = None
    occupation: Optional[str] = Field(None, max_length=200)
    family_doctor: Optional[str] = Field(None, max_length=200, description="Name of family doctor if not at this clinic")
    preferred_pharmacy: Optional[str] = Field(None, max_length=300)
    notes: Optional[str] = Field(None, description="Additional notes about the patient")
    is_active: bool = Field(default=True, description="Whether patient record is active")
    
    # Consent and preferences
    consent_to_treat: bool = Field(default=False)
    consent_to_share_records: bool = Field(default=False)
    preferred_language: str = Field(default="English", max_length=50)
    requires_interpreter: bool = Field(default=False)
    
    @validator('postal_code')
    def validate_postal_code(cls, v):
        # Ensure Canadian postal code format
        v = v.upper().replace(' ', '')
        if len(v) == 6:
            return f"{v[:3]} {v[3:]}"
        raise ValueError('Invalid postal code format')
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        # Check if patient is older than 150 years (data entry error)
        age = (date.today() - v).days / 365.25
        if age > 150:
            raise ValueError('Invalid date of birth - too old')
        return v
    
    @property
    def age(self) -> int:
        """Calculate patient's age"""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    class Config:
        schema_extra = {
            "example": {
                "patient_id": "PAT001",
                "first_name": "Jane",
                "last_name": "Smith",
                "date_of_birth": "1985-06-15",
                "gender": "female",
                "phone": "+14165551234",
                "email": "jane.smith@email.com",
                "address": "123 Main Street",
                "city": "Calgary",
                "province": "AB",
                "postal_code": "T2P 1J9",
                "health_card_number": "1234567890",
                "emergency_contact_name": "John Smith",
                "emergency_contact_phone": "+14165555678",
                "emergency_contact_relationship": "Spouse"
            }
        }


class PatientCreateRequest(BaseModel):
    """Request model for creating a patient"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = None
    date_of_birth: date
    gender: Gender
    phone: str
    email: Optional[EmailStr] = None
    address: str
    city: str
    province: str
    postal_code: str
    health_card_number: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str


class PatientUpdateRequest(BaseModel):
    """Request model for updating a patient"""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    allergies: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    notes: Optional[str] = None


class PatientSearchRequest(BaseModel):
    """Request model for searching patients"""
    search_term: Optional[str] = Field(None, description="Search in name, email, phone")
    health_card_number: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: Optional[bool] = True
