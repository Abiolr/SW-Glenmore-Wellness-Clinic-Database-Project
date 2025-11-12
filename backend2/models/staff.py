"""Staff, Role, and StaffRole models"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
from .base import MongoBaseModel


class RoleType(str, Enum):
    """Role types in the clinic"""
    PHYSICIAN = "physician"
    NURSE_PRACTITIONER = "nurse_practitioner"
    REGISTERED_NURSE = "registered_nurse"
    MIDWIFE = "midwife"
    PHARMACIST = "pharmacist"
    MEDICAL_TECHNICIAN = "medical_technician"
    OFFICE_ADMINISTRATOR = "office_administrator"
    RECEPTIONIST = "receptionist"
    BOOKKEEPER = "bookkeeper"


class Specialization(str, Enum):
    """Medical specializations"""
    PEDIATRICS = "pediatrics"
    INTERNAL_MEDICINE = "internal_medicine"
    MIDWIFERY = "midwifery"
    GENERAL_PRACTICE = "general_practice"


class Staff(MongoBaseModel):
    """Staff collection model"""
    staff_id: str = Field(..., description="Unique staff identifier")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Staff email address")
    phone: str = Field(..., regex="^\\+?[1-9]\\d{1,14}$", description="Phone number in E.164 format")
    address: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[datetime] = None
    hire_date: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether staff member is currently active")
    specialization: Optional[Specialization] = None
    license_number: Optional[str] = Field(None, description="Professional license number")
    emergency_contact: Optional[dict] = Field(None, description="Emergency contact information")
    
    @validator('phone')
    def validate_phone(cls, v):
        # Remove any non-digit characters except + at the beginning
        cleaned = ''.join(c for c in v if c.isdigit() or (c == '+' and v.index(c) == 0))
        if len(cleaned) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        return cleaned
    
    class Config:
        schema_extra = {
            "example": {
                "staff_id": "STF001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@clinic.com",
                "phone": "+14165551234",
                "is_active": True,
                "specialization": "internal_medicine",
                "license_number": "MD123456"
            }
        }


class Role(MongoBaseModel):
    """Role collection model"""
    role_id: str = Field(..., description="Unique role identifier")
    role_name: RoleType = Field(..., description="Name of the role")
    description: Optional[str] = Field(None, max_length=500)
    permissions: List[str] = Field(default_factory=list, description="List of permission codes")
    can_prescribe: bool = Field(default=False, description="Whether role can prescribe medication")
    can_admit_patients: bool = Field(default=False, description="Whether role can admit patients")
    can_order_tests: bool = Field(default=False, description="Whether role can order lab tests")
    can_perform_deliveries: bool = Field(default=False, description="Whether role can perform deliveries")
    is_medical_professional: bool = Field(default=False, description="Whether this is a medical role")
    
    class Config:
        schema_extra = {
            "example": {
                "role_id": "ROL001",
                "role_name": "physician",
                "description": "Licensed medical doctor",
                "permissions": ["view_patients", "edit_patients", "prescribe", "order_tests"],
                "can_prescribe": True,
                "can_admit_patients": True,
                "can_order_tests": True,
                "is_medical_professional": True
            }
        }


class StaffRole(MongoBaseModel):
    """StaffRole junction collection model"""
    staff_id: str = Field(..., description="Reference to Staff")
    role_id: str = Field(..., description="Reference to Role")
    assigned_date: datetime = Field(default_factory=datetime.utcnow)
    assigned_by: str = Field(..., description="Staff ID who assigned this role")
    is_primary: bool = Field(default=False, description="Whether this is the primary role")
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        schema_extra = {
            "example": {
                "staff_id": "STF001",
                "role_id": "ROL001",
                "assigned_date": "2024-01-01T00:00:00",
                "assigned_by": "STF000",
                "is_primary": True
            }
        }


# Response models for API
class StaffWithRoles(Staff):
    """Staff model with roles included"""
    roles: List[Role] = Field(default_factory=list)


class StaffCreateRequest(BaseModel):
    """Request model for creating staff"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    specialization: Optional[Specialization] = None
    license_number: Optional[str] = None
    role_ids: List[str] = Field(..., min_items=1, description="List of role IDs to assign")


class StaffUpdateRequest(BaseModel):
    """Request model for updating staff"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[Specialization] = None
    license_number: Optional[str] = None
    is_active: Optional[bool] = None