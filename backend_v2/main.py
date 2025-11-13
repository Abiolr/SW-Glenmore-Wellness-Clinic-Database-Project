from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, date

from database import Database
from models import *
from crud_patient import PatientCRUD
from crud_staff import StaffCRUD
from crud_appointment import AppointmentCRUD
from crud_visit import VisitCRUD, VisitDiagnosisCRUD, VisitProcedureCRUD
from crud_invoice import InvoiceCRUD, InvoiceLineCRUD, PaymentCRUD
from crud_other import (
    DiagnosisCRUD, ProcedureCRUD, DrugCRUD, PrescriptionCRUD,
    LabTestOrderCRUD, DeliveryCRUD, RecoveryStayCRUD, RecoveryObservationCRUD
)

app = FastAPI(
    title="SW Glenmore Wellness Clinic API",
    description="Backend API for managing clinic operations including patients, appointments, visits, and billing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    """Connect to database on startup"""
    Database.connect_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown"""
    Database.close_db()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SW Glenmore Wellness Clinic API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = Database.get_db()
        db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


# ==================== PATIENT ROUTES ====================

@app.post("/patients", response_model=Patient, status_code=201)
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        return PatientCRUD.create(patient)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/patients", response_model=List[Patient])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all patients with pagination"""
    try:
        return PatientCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int):
    """Get a specific patient by ID"""
    patient = PatientCRUD.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.put("/patients/{patient_id}", response_model=Patient)
async def update_patient(patient_id: int, patient: PatientCreate):
    """Update a patient"""
    updated_patient = PatientCRUD.update(patient_id, patient)
    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated_patient


@app.delete("/patients/{patient_id}", status_code=204)
async def delete_patient(patient_id: int):
    """Delete a patient"""
    if not PatientCRUD.delete(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return None


@app.get("/patients/search/by-name", response_model=List[Patient])
async def search_patients_by_name(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
):
    """Search patients by name"""
    if not first_name and not last_name:
        raise HTTPException(status_code=400, detail="Provide at least one search parameter")
    return PatientCRUD.search_by_name(first_name, last_name)


# ==================== STAFF ROUTES ====================

@app.post("/staff", response_model=Staff, status_code=201)
async def create_staff(staff: StaffCreate):
    """Create a new staff member"""
    try:
        return StaffCRUD.create(staff)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/staff", response_model=List[Staff])
async def get_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = False
):
    """Get all staff members with pagination"""
    try:
        return StaffCRUD.get_all(skip=skip, limit=limit, active_only=active_only)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/staff/{staff_id}", response_model=Staff)
async def get_staff_member(staff_id: int):
    """Get a specific staff member by ID"""
    staff = StaffCRUD.get(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff


@app.put("/staff/{staff_id}", response_model=Staff)
async def update_staff(staff_id: int, staff: StaffCreate):
    """Update a staff member"""
    updated_staff = StaffCRUD.update(staff_id, staff)
    if not updated_staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return updated_staff


@app.delete("/staff/{staff_id}", status_code=204)
async def delete_staff(staff_id: int):
    """Delete a staff member"""
    if not StaffCRUD.delete(staff_id):
        raise HTTPException(status_code=404, detail="Staff member not found")
    return None


@app.put("/staff/{staff_id}/deactivate", response_model=Staff)
async def deactivate_staff(staff_id: int):
    """Deactivate a staff member"""
    staff = StaffCRUD.deactivate(staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff


# ==================== APPOINTMENT ROUTES ====================

@app.post("/appointments", response_model=Appointment, status_code=201)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment"""
    try:
        return AppointmentCRUD.create(appointment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all appointments with pagination"""
    try:
        return AppointmentCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: int):
    """Get a specific appointment by ID"""
    appointment = AppointmentCRUD.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@app.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: int, appointment: AppointmentCreate):
    """Update an appointment"""
    updated_appointment = AppointmentCRUD.update(appointment_id, appointment)
    if not updated_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return updated_appointment


@app.delete("/appointments/{appointment_id}", status_code=204)
async def delete_appointment(appointment_id: int):
    """Delete an appointment"""
    if not AppointmentCRUD.delete(appointment_id):
        raise HTTPException(status_code=404, detail="Appointment not found")
    return None


@app.get("/appointments/patient/{patient_id}", response_model=List[Appointment])
async def get_appointments_by_patient(patient_id: int):
    """Get all appointments for a specific patient"""
    return AppointmentCRUD.get_by_patient(patient_id)


@app.get("/appointments/staff/{staff_id}", response_model=List[Appointment])
async def get_appointments_by_staff(
    staff_id: int,
    date: Optional[date] = None
):
    """Get all appointments for a specific staff member, optionally filtered by date"""
    return AppointmentCRUD.get_by_staff(staff_id, date)


# ==================== VISIT ROUTES ====================

@app.post("/visits", response_model=Visit, status_code=201)
async def create_visit(visit: VisitCreate):
    """Create a new visit"""
    try:
        return VisitCRUD.create(visit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/visits", response_model=List[Visit])
async def get_visits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all visits with pagination"""
    try:
        return VisitCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visits/{visit_id}", response_model=Visit)
async def get_visit(visit_id: int):
    """Get a specific visit by ID"""
    visit = VisitCRUD.get(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@app.put("/visits/{visit_id}", response_model=Visit)
async def update_visit(visit_id: int, visit: VisitCreate):
    """Update a visit"""
    updated_visit = VisitCRUD.update(visit_id, visit)
    if not updated_visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return updated_visit


@app.delete("/visits/{visit_id}", status_code=204)
async def delete_visit(visit_id: int):
    """Delete a visit"""
    if not VisitCRUD.delete(visit_id):
        raise HTTPException(status_code=404, detail="Visit not found")
    return None


@app.get("/visits/patient/{patient_id}", response_model=List[Visit])
async def get_visits_by_patient(patient_id: int):
    """Get all visits for a specific patient"""
    return VisitCRUD.get_by_patient(patient_id)


# ==================== VISIT DIAGNOSIS ROUTES ====================

@app.post("/visits/{visit_id}/diagnoses", response_model=VisitDiagnosis, status_code=201)
async def add_diagnosis_to_visit(visit_id: int, diagnosis_id: int, is_primary: bool = False):
    """Add a diagnosis to a visit"""
    try:
        visit_diagnosis = VisitDiagnosisCreate(
            visit_id=visit_id,
            diagnosis_id=diagnosis_id,
            is_primary=is_primary
        )
        return VisitDiagnosisCRUD.create(visit_diagnosis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/visits/{visit_id}/diagnoses", response_model=List[VisitDiagnosis])
async def get_visit_diagnoses(visit_id: int):
    """Get all diagnoses for a specific visit"""
    return VisitDiagnosisCRUD.get_by_visit(visit_id)


@app.delete("/visits/{visit_id}/diagnoses/{diagnosis_id}", status_code=204)
async def remove_diagnosis_from_visit(visit_id: int, diagnosis_id: int):
    """Remove a diagnosis from a visit"""
    if not VisitDiagnosisCRUD.delete(visit_id, diagnosis_id):
        raise HTTPException(status_code=404, detail="Visit diagnosis not found")
    return None


# ==================== VISIT PROCEDURE ROUTES ====================

@app.post("/visits/{visit_id}/procedures", response_model=VisitProcedure, status_code=201)
async def add_procedure_to_visit(visit_id: int, procedure_id: int, fee: float):
    """Add a procedure to a visit"""
    try:
        visit_procedure = VisitProcedureCreate(
            visit_id=visit_id,
            procedure_id=procedure_id,
            fee=fee
        )
        return VisitProcedureCRUD.create(visit_procedure)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/visits/{visit_id}/procedures", response_model=List[VisitProcedure])
async def get_visit_procedures(visit_id: int):
    """Get all procedures for a specific visit"""
    return VisitProcedureCRUD.get_by_visit(visit_id)


@app.delete("/visits/{visit_id}/procedures/{procedure_id}", status_code=204)
async def remove_procedure_from_visit(visit_id: int, procedure_id: int):
    """Remove a procedure from a visit"""
    if not VisitProcedureCRUD.delete(visit_id, procedure_id):
        raise HTTPException(status_code=404, detail="Visit procedure not found")
    return None


# ==================== DIAGNOSIS ROUTES ====================

@app.post("/diagnoses", response_model=Diagnosis, status_code=201)
async def create_diagnosis(diagnosis: DiagnosisCreate):
    """Create a new diagnosis"""
    try:
        return DiagnosisCRUD.create(diagnosis)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/diagnoses", response_model=List[Diagnosis])
async def get_diagnoses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all diagnoses with pagination"""
    try:
        return DiagnosisCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/diagnoses/{diagnosis_id}", response_model=Diagnosis)
async def get_diagnosis(diagnosis_id: int):
    """Get a specific diagnosis by ID"""
    diagnosis = DiagnosisCRUD.get(diagnosis_id)
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return diagnosis


@app.get("/diagnoses/search/{code}", response_model=List[Diagnosis])
async def search_diagnoses_by_code(code: str):
    """Search diagnoses by code"""
    return DiagnosisCRUD.search_by_code(code)


# ==================== PROCEDURE ROUTES ====================

@app.post("/procedures", response_model=Procedure, status_code=201)
async def create_procedure(procedure: ProcedureCreate):
    """Create a new procedure"""
    try:
        return ProcedureCRUD.create(procedure)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/procedures", response_model=List[Procedure])
async def get_procedures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all procedures with pagination"""
    try:
        return ProcedureCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/procedures/{procedure_id}", response_model=Procedure)
async def get_procedure(procedure_id: int):
    """Get a specific procedure by ID"""
    procedure = ProcedureCRUD.get(procedure_id)
    if not procedure:
        raise HTTPException(status_code=404, detail="Procedure not found")
    return procedure


# ==================== DRUG ROUTES ====================

@app.post("/drugs", response_model=Drug, status_code=201)
async def create_drug(drug: DrugCreate):
    """Create a new drug"""
    try:
        return DrugCRUD.create(drug)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/drugs", response_model=List[Drug])
async def get_drugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all drugs with pagination"""
    try:
        return DrugCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/drugs/{drug_id}", response_model=Drug)
async def get_drug(drug_id: int):
    """Get a specific drug by ID"""
    drug = DrugCRUD.get(drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug


@app.get("/drugs/search/{name}", response_model=List[Drug])
async def search_drugs_by_name(name: str):
    """Search drugs by brand name"""
    return DrugCRUD.search_by_name(name)


# ==================== PRESCRIPTION ROUTES ====================

@app.post("/prescriptions", response_model=Prescription, status_code=201)
async def create_prescription(prescription: PrescriptionCreate):
    """Create a new prescription"""
    try:
        return PrescriptionCRUD.create(prescription)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/prescriptions/{prescription_id}", response_model=Prescription)
async def get_prescription(prescription_id: int):
    """Get a specific prescription by ID"""
    prescription = PrescriptionCRUD.get(prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription


@app.get("/prescriptions/visit/{visit_id}", response_model=List[Prescription])
async def get_prescriptions_by_visit(visit_id: int):
    """Get all prescriptions for a specific visit"""
    return PrescriptionCRUD.get_by_visit(visit_id)


# ==================== LAB TEST ORDER ROUTES ====================

@app.post("/lab-tests", response_model=LabTestOrder, status_code=201)
async def create_lab_test(lab_test: LabTestOrderCreate):
    """Create a new lab test order"""
    try:
        return LabTestOrderCRUD.create(lab_test)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/lab-tests/{labtest_id}", response_model=LabTestOrder)
async def get_lab_test(labtest_id: int):
    """Get a specific lab test by ID"""
    lab_test = LabTestOrderCRUD.get(labtest_id)
    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")
    return lab_test


@app.get("/lab-tests/visit/{visit_id}", response_model=List[LabTestOrder])
async def get_lab_tests_by_visit(visit_id: int):
    """Get all lab tests for a specific visit"""
    return LabTestOrderCRUD.get_by_visit(visit_id)


# ==================== DELIVERY ROUTES ====================

@app.post("/deliveries", response_model=Delivery, status_code=201)
async def create_delivery(delivery: DeliveryCreate):
    """Create a new delivery record"""
    try:
        return DeliveryCRUD.create(delivery)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/deliveries/visit/{visit_id}", response_model=Delivery)
async def get_delivery_by_visit(visit_id: int):
    """Get delivery record by visit ID"""
    delivery = DeliveryCRUD.get_by_visit(visit_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery


# ==================== RECOVERY STAY ROUTES ====================

@app.post("/recovery-stays", response_model=RecoveryStay, status_code=201)
async def create_recovery_stay(recovery_stay: RecoveryStayCreate):
    """Create a new recovery stay"""
    try:
        return RecoveryStayCRUD.create(recovery_stay)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/recovery-stays/{stay_id}", response_model=RecoveryStay)
async def get_recovery_stay(stay_id: int):
    """Get a specific recovery stay by ID"""
    stay = RecoveryStayCRUD.get(stay_id)
    if not stay:
        raise HTTPException(status_code=404, detail="Recovery stay not found")
    return stay


# ==================== RECOVERY OBSERVATION ROUTES ====================

@app.post("/recovery-observations", response_model=RecoveryObservation, status_code=201)
async def create_recovery_observation(observation: RecoveryObservationCreate):
    """Create a new recovery observation"""
    try:
        return RecoveryObservationCRUD.create(observation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/recovery-observations/stay/{stay_id}", response_model=List[RecoveryObservation])
async def get_recovery_observations_by_stay(stay_id: int):
    """Get all observations for a specific recovery stay"""
    return RecoveryObservationCRUD.get_by_stay(stay_id)


# ==================== INVOICE ROUTES ====================

@app.post("/invoices", response_model=Invoice, status_code=201)
async def create_invoice(invoice: InvoiceCreate):
    """Create a new invoice"""
    try:
        return InvoiceCRUD.create(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None
):
    """Get all invoices with pagination, optionally filtered by status"""
    try:
        if status:
            return InvoiceCRUD.get_by_status(status)
        return InvoiceCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: int):
    """Get a specific invoice by ID"""
    invoice = InvoiceCRUD.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@app.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: int, invoice: InvoiceCreate):
    """Update an invoice"""
    updated_invoice = InvoiceCRUD.update(invoice_id, invoice)
    if not updated_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated_invoice


@app.put("/invoices/{invoice_id}/status", response_model=Invoice)
async def update_invoice_status(invoice_id: int, status: str):
    """Update invoice status"""
    updated_invoice = InvoiceCRUD.update_status(invoice_id, status)
    if not updated_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated_invoice


@app.delete("/invoices/{invoice_id}", status_code=204)
async def delete_invoice(invoice_id: int):
    """Delete an invoice"""
    if not InvoiceCRUD.delete(invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None


@app.get("/invoices/patient/{patient_id}", response_model=List[Invoice])
async def get_invoices_by_patient(patient_id: int):
    """Get all invoices for a specific patient"""
    return InvoiceCRUD.get_by_patient(patient_id)


# ==================== INVOICE LINE ROUTES ====================

@app.post("/invoices/{invoice_id}/lines", response_model=InvoiceLine, status_code=201)
async def add_invoice_line(invoice_id: int, line: InvoiceLineCreate):
    """Add a line item to an invoice"""
    try:
        return InvoiceLineCRUD.create(line)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/invoices/{invoice_id}/lines", response_model=List[InvoiceLine])
async def get_invoice_lines(invoice_id: int):
    """Get all line items for a specific invoice"""
    return InvoiceLineCRUD.get_by_invoice(invoice_id)


@app.delete("/invoices/{invoice_id}/lines/{line_no}", status_code=204)
async def delete_invoice_line(invoice_id: int, line_no: int):
    """Remove a line item from an invoice"""
    if not InvoiceLineCRUD.delete(invoice_id, line_no):
        raise HTTPException(status_code=404, detail="Invoice line not found")
    return None


# ==================== PAYMENT ROUTES ====================

@app.post("/payments", response_model=Payment, status_code=201)
async def create_payment(payment: PaymentCreate):
    """Create a new payment"""
    try:
        return PaymentCRUD.create(payment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/payments", response_model=List[Payment])
async def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all payments with pagination"""
    try:
        return PaymentCRUD.get_all(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments/{payment_id}", response_model=Payment)
async def get_payment(payment_id: int):
    """Get a specific payment by ID"""
    payment = PaymentCRUD.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@app.delete("/payments/{payment_id}", status_code=204)
async def delete_payment(payment_id: int):
    """Delete a payment"""
    if not PaymentCRUD.delete(payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")
    return None


@app.get("/payments/patient/{patient_id}", response_model=List[Payment])
async def get_payments_by_patient(patient_id: int):
    """Get all payments for a specific patient"""
    return PaymentCRUD.get_by_patient(patient_id)


@app.get("/payments/invoice/{invoice_id}", response_model=List[Payment])
async def get_payments_by_invoice(invoice_id: int):
    """Get all payments for a specific invoice"""
    return PaymentCRUD.get_by_invoice(invoice_id)
