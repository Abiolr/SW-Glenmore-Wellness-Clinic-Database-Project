from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal


# Patient Model
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    phone: str
    email: Optional[EmailStr] = None
    gov_card_no: Optional[str] = None
    insurance_no: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    patient_id: int
    
    class Config:
        from_attributes = True


# Staff Model
class StaffBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    active: bool = True

class StaffCreate(StaffBase):
    pass

class Staff(StaffBase):
    staff_id: int
    
    class Config:
        from_attributes = True


# Role Model
class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    role_id: int
    
    class Config:
        from_attributes = True


# StaffRole Model
class StaffRoleBase(BaseModel):
    staff_id: int
    role_id: int

class StaffRoleCreate(StaffRoleBase):
    pass

class StaffRole(StaffRoleBase):
    pass
    
    class Config:
        from_attributes = True


# WeeklyCoverage Model
class WeeklyCoverageBase(BaseModel):
    coverage_id: Optional[int] = None
    staff_id: int
    week_start: date
    on_call_phone: Optional[str] = None
    notes: Optional[str] = None

class WeeklyCoverageCreate(WeeklyCoverageBase):
    pass

class WeeklyCoverage(WeeklyCoverageBase):
    coverage_id: int
    
    class Config:
        from_attributes = True


# PractitionerDailySchedule Model
class PractitionerDailyScheduleBase(BaseModel):
    schedule_id: Optional[int] = None
    staff_id: int
    work_date: date
    slot_start: datetime
    slot_end: datetime
    is_walkin: bool = False

class PractitionerDailyScheduleCreate(PractitionerDailyScheduleBase):
    pass

class PractitionerDailySchedule(PractitionerDailyScheduleBase):
    schedule_id: int
    
    class Config:
        from_attributes = True


# Appointment Model
class AppointmentBase(BaseModel):
    appointment_id: Optional[int] = None
    patient_id: int
    staff_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    created_at: Optional[datetime] = None
    is_walkin: bool = False

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    appointment_id: int
    
    class Config:
        from_attributes = True


# Visit Model
class VisitBase(BaseModel):
    visit_id: Optional[int] = None
    patient_id: int
    staff_id: int
    appointment_id: Optional[int] = None
    visit_type: str  # "checkup", "immunization", "illness", "prenatal", "postnatal"
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class Visit(VisitBase):
    visit_id: int
    
    class Config:
        from_attributes = True


# Diagnosis Model
class DiagnosisBase(BaseModel):
    diagnosis_id: Optional[int] = None
    code: str
    description: str

class DiagnosisCreate(DiagnosisBase):
    pass

class Diagnosis(DiagnosisBase):
    diagnosis_id: int
    
    class Config:
        from_attributes = True


# VisitDiagnosis Model
class VisitDiagnosisBase(BaseModel):
    visit_id: int
    diagnosis_id: int
    is_primary: bool = False

class VisitDiagnosisCreate(VisitDiagnosisBase):
    pass

class VisitDiagnosis(VisitDiagnosisBase):
    pass
    
    class Config:
        from_attributes = True


# Procedure Model
class ProcedureBase(BaseModel):
    procedure_id: Optional[int] = None
    code: str
    description: str
    default_fee: Optional[float] = None

class ProcedureCreate(ProcedureBase):
    pass

class Procedure(ProcedureBase):
    procedure_id: int
    
    class Config:
        from_attributes = True


# VisitProcedure Model
class VisitProcedureBase(BaseModel):
    visit_id: int
    procedure_id: int
    fee: float

class VisitProcedureCreate(VisitProcedureBase):
    pass

class VisitProcedure(VisitProcedureBase):
    pass
    
    class Config:
        from_attributes = True


# Drug Model
class DrugBase(BaseModel):
    drug_id: Optional[int] = None
    brand_name: str
    strength_form: str  # e.g., "500mg tablet"
    generic_name: Optional[str] = None

class DrugCreate(DrugBase):
    pass

class Drug(DrugBase):
    drug_id: int
    
    class Config:
        from_attributes = True


# Prescription Model
class PrescriptionBase(BaseModel):
    prescription_id: Optional[int] = None
    visit_id: int
    drug_id: int
    name_on_label: Optional[str] = None
    dispensed_by: Optional[int] = None  # Staff ID
    dispensed_at: Optional[datetime] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class Prescription(PrescriptionBase):
    prescription_id: int
    
    class Config:
        from_attributes = True


# LabTestOrder Model
class LabTestOrderBase(BaseModel):
    labtest_id: Optional[int] = None
    visit_id: int
    ordered_by: int  # Staff ID
    test_name: str
    performed_by: Optional[int] = None  # Staff ID
    result_at: Optional[datetime] = None
    notes: Optional[str] = None

class LabTestOrderCreate(LabTestOrderBase):
    pass

class LabTestOrder(LabTestOrderBase):
    labtest_id: int
    
    class Config:
        from_attributes = True


# Delivery Model
class DeliveryBase(BaseModel):
    delivery_id: Optional[int] = None
    visit_id: int
    performed_by: int  # Staff ID

class DeliveryCreate(DeliveryBase):
    pass

class Delivery(DeliveryBase):
    delivery_id: int
    
    class Config:
        from_attributes = True


# RecoveryStay Model (corrected from RecovertStay)
class RecoveryStayBase(BaseModel):
    stay_id: Optional[int] = None
    patient_id: int
    admit_time: datetime
    discharge_time: Optional[datetime] = None

class RecoveryStayCreate(RecoveryStayBase):
    pass

class RecoveryStay(RecoveryStayBase):
    stay_id: int
    
    class Config:
        from_attributes = True


# RecoveryObservation Model
class RecoveryObservationBase(BaseModel):
    stay_id: int
    text_on: datetime
    observed_at: Optional[datetime] = None
    notes: str

class RecoveryObservationCreate(RecoveryObservationBase):
    pass

class RecoveryObservation(RecoveryObservationBase):
    pass
    
    class Config:
        from_attributes = True


# Invoice Model
class InvoiceBase(BaseModel):
    invoice_id: Optional[int] = None
    patient_id: int
    invoice_date: date
    status: str  # "pending", "paid", "partial"

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    invoice_id: int
    
    class Config:
        from_attributes = True


# InvoiceLine Model
class InvoiceLineBase(BaseModel):
    invoice_id: int
    item_ref_id: int  # Reference to Visit, Prescription, etc.
    description: str
    qty: int = 1
    unit_price: float

class InvoiceLineCreate(InvoiceLineBase):
    pass

class InvoiceLine(InvoiceLineBase):
    line_no: int
    
    class Config:
        from_attributes = True


# Payment Model
class PaymentBase(BaseModel):
    payment_id: Optional[int] = None
    patient_id: int
    invoice_id: Optional[int] = None
    payment_date: date
    method: str  # "cash", "insurance", "government"
    amount: float

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    payment_id: int
    
    class Config:
        from_attributes = True
