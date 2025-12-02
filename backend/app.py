from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date
import logging
import traceback
from clinic_api.database import Database
from clinic_api.models import *
from clinic_api.services.patient import PatientCRUD
from clinic_api.services.staff import StaffCRUD
from clinic_api.services.appointment import AppointmentCRUD
from clinic_api.services.visit import VisitCRUD, VisitDiagnosisCRUD, VisitProcedureCRUD
from clinic_api.services.invoice import InvoiceCRUD, InvoiceLineCRUD, PaymentCRUD
from clinic_api.services.Views import initialize_views, recreate_all_views, get_database
from clinic_api.services.stored_procedures_aggregation import initialize_aggregation_functions, agg_functions
from clinic_api.services.other import (
    DiagnosisCRUD, ProcedureCRUD, DrugCRUD, PrescriptionCRUD,
    LabTestOrderCRUD, DeliveryCRUD, RecoveryStayCRUD, RecoveryObservationCRUD
)
from clinic_api.services.weekly_coverage import StaffAssignmentCRUD
from clinic_api.services.reports import ReportService, _sanitize_for_json
from clinic_api.services.scheduling import StaffShiftCRUD, StaffShiftCreate
from clinic_api.services.billing import InsurerCRUD, InsurerCreate

app = Flask(__name__)
db = get_database()
# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to database when app starts
with app.app_context():
    Database.connect_db()

def handle_error(e):
    """Generic error handler"""
    return jsonify({"error": str(e)}), 500

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ROOT & HEALTH ROUTES ====================
@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "SW Glenmore Wellness Clinic API",
        "version": "1.0.0",
        "status": "active"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = Database.get_db()
        db.command('ping')
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route('/connect', methods=['GET', 'POST'])
def connect_with_token():
    """Safe token-based connect endpoint.

    Expects a token either as query parameter `?token=...` or in JSON body { token: '...' }.
    This endpoint will try to locate the token in common token/session collections and
    return a friendly error instead of raising a 500 when the DB query fails or the
    token is missing.
    """
    try:
        # Get token from query or JSON body
        token = request.args.get('token')
        if not token and request.is_json:
            token = request.get_json(silent=True) and request.get_json().get('token')

        if not token:
            return jsonify({'error': 'token parameter required'}), 400

        # Try common token collection names (adjust if your project uses a different name)
        candidate_collections = ['auth_tokens', 'tokens', 'sessions', 'api_tokens']
        found = None
        for coll_name in candidate_collections:
            if coll_name in db.list_collection_names():
                doc = db[coll_name].find_one({'token': token}, {'_id': 0})
                if doc:
                    found = {'collection': coll_name, 'document': doc}
                    break

        # If not found, try a more general lookup across 'users' or 'sessions' by token key
        if not found:
            # Example: some apps store tokens on the user document under 'api_token' or similar
            if 'users' in db.list_collection_names():
                user_doc = db['users'].find_one({'api_token': token}, {'_id': 0})
                if user_doc:
                    found = {'collection': 'users', 'document': user_doc}

        if not found:
            return jsonify({'error': 'token not found'}), 404

        return jsonify({'status': 'ok', 'source': found['collection'], 'data': found['document']}), 200

    except Exception as e:
        # Log exception and return safe error response instead of crashing
        logger.exception('Error in /connect endpoint')
        return jsonify({'error': 'internal server error', 'detail': str(e)}), 500


# ============================================
# INITIALIZE VIEWS ON STARTUP (AUTO-CREATE!)
# ============================================
logger.info("Initializing MongoDB views...")
try:
    views_manager = initialize_views()
    logger.info("Views initialization complete")
except Exception:
    logger.exception("Failed to initialize MongoDB views; continuing without pre-created views")
    views_manager = None


# ============================================
# VIEW ENDPOINTS
# ============================================

# View 1: Patient Full Details
@app.route('/api/views/patients/full-details', methods=['GET'])
def get_patient_full_details():
    """Get all patients with visit statistics"""
    try:
        patients = list(db.patient_full_details.find({}))
        return jsonify(patients), 200
    except Exception as e:
        logger.error(f"Error fetching patient full details: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/views/patients/active', methods=['GET'])
def get_active_patients():
    """Get patients with active visits"""
    try:
        patients = list(db.patient_full_details.find({'has_active_visits': True}))
        return jsonify(patients), 200
    except Exception as e:
        logger.error(f"Error fetching active patients: {e}")
        return jsonify({'error': str(e)}), 500


# View 2: Staff Appointments Summary
@app.route('/api/views/staff/summary', methods=['GET'])
def get_staff_summary():
    """Get staff workload summary"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        if active_only:
            staff = list(db.staff_appointments_summary.find({'active': True}))
        else:
            staff = list(db.staff_appointments_summary.find())
        
        return jsonify(staff), 200
    except Exception as e:
        logger.error(f"Error fetching staff summary: {e}")
        return jsonify({'error': str(e)}), 500


# View 3: Active Visits Overview
@app.route('/api/views/visits/active', methods=['GET'])
def get_active_visits():
    """Get all currently active visits (not completed)"""
    try:
        visits = list(db.active_visits_overview.find())
        return jsonify(visits), 200
    except Exception as e:
        logger.error(f"Error fetching active visits: {e}")
        return jsonify({'error': str(e)}), 500


# View 4: Invoice Payment Summary
@app.route('/api/views/invoices/summary', methods=['GET'])
def get_invoice_summary():
    """Get invoice overview with payment details"""
    try:
        invoices = list(db.invoice_payment_summary.find())
        return jsonify(invoices), 200
    except Exception as e:
        logger.error(f"Error fetching invoice summary: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/views/invoices/unpaid', methods=['GET'])
def get_unpaid_invoices():
    """Get invoices that are not fully paid"""
    try:
        invoices = list(db.invoice_payment_summary.find({'is_fully_paid': False}))
        return jsonify(invoices), 200
    except Exception as e:
        logger.error(f"Error fetching unpaid invoices: {e}")
        return jsonify({'error': str(e)}), 500


# View 5: Appointment Calendar View
@app.route('/api/views/appointments/calendar', methods=['GET'])
def get_calendar_appointments():
    """Get appointments formatted for calendar display"""
    try:
        appointments = list(db.appointment_calendar_view.find())
        return jsonify(appointments), 200
    except Exception as e:
        logger.error(f"Error fetching calendar appointments: {e}")
        return jsonify({'error': str(e)}), 500


# Admin: Check views status
@app.route('/api/views/status', methods=['GET'])
def get_views_status():
    """Check status of all MongoDB views"""
    try:
        collections = db.list_collection_names()
        views = [
            'patient_full_details',
            'staff_appointments_summary',
            'active_visits_overview',
            'invoice_payment_summary',
            'appointment_calendar_view'
        ]
        
        status = {}
        for view in views:
            exists = view in collections
            count = db[view].count_documents({}) if exists else 0
            status[view] = {
                'exists': exists,
                'document_count': count
            }
        
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error checking views status: {e}")
        return jsonify({'error': str(e)}), 500


# Admin: Force recreate views
@app.route('/api/views/recreate', methods=['POST'])
def recreate_views():
    """Force recreation of all views (admin endpoint)"""
    try:
        results = recreate_all_views()  # ← No need to pass db anymore!
        
        success_count = sum(1 for v in results.values() if v)
        
        return jsonify({
            'message': f'Recreated {success_count}/{len(results)} views',
            'results': results
        }), 200
    except Exception as e:
        logger.error(f"Error recreating views: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# Stored Procedure ENDPOINTS
# ============================================

try:
    functions = initialize_aggregation_functions()
    aggregation_ready = True
    logger.info("Aggregation functions initialized")
except Exception:
    logger.exception("Failed to initialize aggregation functions; stored aggregation endpoints may be unavailable")
    functions = None
    aggregation_ready = False

@app.route('/api/invoices/<int:invoice_id>/summary', methods=['GET'])
def get_invoice_summary_endpoint(invoice_id):
    """
    Get complete invoice summary with line items in ONE query
    
    Usage:
    GET http://localhost:8000/api/invoices/1/summary
    
    Response:
    {
      "invoice_id": 1,
      "invoice_date": "2024-01-15",
      "status": "paid",
      "patient_id": 1,
      "total_amount": 250.50,
      "line_count": 5,
      "items": [
        {
          "description": "Consultation",
          "qty": 1,
          "unit_price": 100.00,
          "line_total": 100.00
        },
        {
          "description": "Lab Test",
          "qty": 3,
          "unit_price": 50.00,
          "line_total": 150.00
        }
      ]
    }
    """
    # If aggregation functions failed to initialize, return 503
    if not globals().get('aggregation_ready', False):
        return jsonify({'error': 'aggregation functions not available', 'detail': 'server initialization incomplete'}), 503

    try:
        # This ONE function gets invoice + all line items in one query!
        summary = agg_functions.get_invoice_summary(invoice_id)

        if not summary:
            return jsonify({'error': 'Invoice not found'}), 404

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"Error getting invoice summary: {e}")
        return jsonify({'error': str(e)}), 500


  
# ==================== PATIENT ROUTES ====================
@app.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        patient = PatientCreate(**data)
        result = PatientCRUD.create(patient)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/patients', methods=['GET'])
def get_patients():
    """Get all patients with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        patients = PatientCRUD.get_all(skip=skip, limit=limit)
        return jsonify([p.model_dump(mode='json') for p in patients])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a specific patient by ID"""
    patient = PatientCRUD.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient.model_dump(mode='json'))

@app.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient"""
    try:
        data = request.get_json()
        patient = PatientCreate(**data)
        updated_patient = PatientCRUD.update(patient_id, patient)
        if not updated_patient:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(updated_patient.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    if not PatientCRUD.delete(patient_id):
        return jsonify({"error": "Patient not found"}), 404
    return '', 204

@app.route('/patients/search/by-name', methods=['GET'])
def search_patients_by_name():
    """Search patients by name"""
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    
    if not first_name and not last_name:
        return jsonify({"error": "Provide at least one search parameter"}), 400
    
    patients = PatientCRUD.search_by_name(first_name, last_name)
    return jsonify([p.model_dump(mode='json') for p in patients])

# ==================== STAFF ROUTES ====================
@app.route('/staff', methods=['POST'])
def create_staff():
    """Create a new staff member"""
    try:
        data = request.get_json()
        staff = StaffCreate(**data)
        result = StaffCRUD.create(staff)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/staff', methods=['GET'])
def get_staff():
    """Get all staff members with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        staff_list = StaffCRUD.get_all(skip=skip, limit=limit, active_only=active_only)
        return jsonify([s.model_dump(mode='json') for s in staff_list])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/staff/<int:staff_id>', methods=['GET'])
def get_staff_member(staff_id):
    """Get a specific staff member by ID"""
    staff = StaffCRUD.get(staff_id)
    if not staff:
        return jsonify({"error": "Staff member not found"}), 404
    return jsonify(staff.model_dump(mode='json'))

@app.route('/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update a staff member"""
    try:
        data = request.get_json()
        staff = StaffCreate(**data)
        updated_staff = StaffCRUD.update(staff_id, staff)
        if not updated_staff:
            return jsonify({"error": "Staff member not found"}), 404
        return jsonify(updated_staff.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Delete a staff member"""
    if not StaffCRUD.delete(staff_id):
        return jsonify({"error": "Staff member not found"}), 404
    return '', 204

@app.route('/staff/<int:staff_id>/deactivate', methods=['PUT'])
def deactivate_staff(staff_id):
    """Deactivate a staff member"""
    staff = StaffCRUD.deactivate(staff_id)
    if not staff:
        return jsonify({"error": "Staff member not found"}), 404
    return jsonify(staff.model_dump(mode='json'))

# ==================== APPOINTMENT ROUTES ====================
@app.route('/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.get_json()
        appointment = AppointmentCreate(**data)
        result = AppointmentCRUD.create(appointment)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        appointments = AppointmentCRUD.get_all(skip=skip, limit=limit)
        return jsonify([a.model_dump(mode='json') for a in appointments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    """Get a specific appointment by ID"""
    appointment = AppointmentCRUD.get(appointment_id)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(appointment.model_dump(mode='json'))

@app.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        data = request.get_json()
        appointment = AppointmentCreate(**data)
        updated_appointment = AppointmentCRUD.update(appointment_id, appointment)
        if not updated_appointment:
            return jsonify({"error": "Appointment not found"}), 404
        return jsonify(updated_appointment.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    """Delete an appointment"""
    if not AppointmentCRUD.delete(appointment_id):
        return jsonify({"error": "Appointment not found"}), 404
    return '', 204

@app.route('/appointments/patient/<int:patient_id>', methods=['GET'])
def get_appointments_by_patient(patient_id):
    """Get all appointments for a specific patient"""
    appointments = AppointmentCRUD.get_by_patient(patient_id)
    return jsonify([a.model_dump(mode='json') for a in appointments])

@app.route('/appointments/staff/<int:staff_id>', methods=['GET'])
def get_appointments_by_staff(staff_id):
    """Get all appointments for a specific staff member"""
    date_filter = request.args.get('date')
    if date_filter:
        date_filter = date.fromisoformat(date_filter)
    
    appointments = AppointmentCRUD.get_by_staff(staff_id, date_filter)
    return jsonify([a.model_dump(mode='json') for a in appointments])

# ==================== VISIT ROUTES ====================
@app.route('/visits', methods=['POST'])
def create_visit():
    """Create a new visit"""
    try:
        data = request.get_json()
        visit = VisitCreate(**data)
        result = VisitCRUD.create(visit)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/visits', methods=['GET'])
def get_visits():
    """Get all visits with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        visits = VisitCRUD.get_all(skip=skip, limit=limit)
        return jsonify([v.model_dump(mode='json') for v in visits])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/visits/<int:visit_id>', methods=['GET'])
def get_visit(visit_id):
    """Get a specific visit by ID"""
    visit = VisitCRUD.get(visit_id)
    if not visit:
        return jsonify({"error": "Visit not found"}), 404
    return jsonify(visit.model_dump(mode='json'))

@app.route('/visits/<int:visit_id>', methods=['PUT'])
def update_visit(visit_id):
    """Update a visit"""
    try:
        data = request.get_json()
        visit = VisitCreate(**data)
        updated_visit = VisitCRUD.update(visit_id, visit)
        if not updated_visit:
            return jsonify({"error": "Visit not found"}), 404
        return jsonify(updated_visit.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/visits/<int:visit_id>', methods=['DELETE'])
def delete_visit(visit_id):
    """Delete a visit"""
    if not VisitCRUD.delete(visit_id):
        return jsonify({"error": "Visit not found"}), 404
    return '', 204

@app.route('/visits/patient/<int:patient_id>', methods=['GET'])
def get_visits_by_patient(patient_id):
    """Get all visits for a specific patient"""
    visits = VisitCRUD.get_by_patient(patient_id)
    return jsonify([v.model_dump(mode='json') for v in visits])

# ==================== VISIT DIAGNOSIS ROUTES ====================
@app.route('/visits/<int:visit_id>/diagnoses', methods=['POST'])
def add_diagnosis_to_visit(visit_id):
    """Add a diagnosis to a visit"""
    try:
        data = request.get_json()
        diagnosis_id = data.get('diagnosis_id')
        is_primary = data.get('is_primary', False)
        
        visit_diagnosis = VisitDiagnosisCreate(
            visit_id=visit_id,
            diagnosis_id=diagnosis_id,
            is_primary=is_primary
        )
        result = VisitDiagnosisCRUD.create(visit_diagnosis)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/visits/<int:visit_id>/diagnoses', methods=['GET'])
def get_visit_diagnoses(visit_id):
    """Get all diagnoses for a specific visit"""
    diagnoses = VisitDiagnosisCRUD.get_by_visit(visit_id)
    return jsonify([d.model_dump(mode='json') for d in diagnoses])

@app.route('/visits/<int:visit_id>/diagnoses/<int:diagnosis_id>', methods=['DELETE'])
def remove_diagnosis_from_visit(visit_id, diagnosis_id):
    """Remove a diagnosis from a visit"""
    if not VisitDiagnosisCRUD.delete(visit_id, diagnosis_id):
        return jsonify({"error": "Visit diagnosis not found"}), 404
    return '', 204

# ==================== VISIT PROCEDURE ROUTES ====================
@app.route('/visits/<int:visit_id>/procedures', methods=['POST'])
def add_procedure_to_visit(visit_id):
    """Add a procedure to a visit"""
    try:
        data = request.get_json()
        procedure_id = data.get('procedure_id')
        fee = data.get('fee')
        
        visit_procedure = VisitProcedureCreate(
            visit_id=visit_id,
            procedure_id=procedure_id,
            fee=fee
        )
        result = VisitProcedureCRUD.create(visit_procedure)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/visits/<int:visit_id>/procedures', methods=['GET'])
def get_visit_procedures(visit_id):
    """Get all procedures for a specific visit"""
    procedures = VisitProcedureCRUD.get_by_visit(visit_id)
    return jsonify([p.model_dump(mode='json') for p in procedures])

@app.route('/visits/<int:visit_id>/procedures/<int:procedure_id>', methods=['DELETE'])
def remove_procedure_from_visit(visit_id, procedure_id):
    """Remove a procedure from a visit"""
    if not VisitProcedureCRUD.delete(visit_id, procedure_id):
        return jsonify({"error": "Visit procedure not found"}), 404
    return '', 204

# ==================== DIAGNOSIS ROUTES ====================
@app.route('/diagnoses', methods=['POST'])
def create_diagnosis():
    """Create a new diagnosis"""
    try:
        data = request.get_json()
        diagnosis = DiagnosisCreate(**data)
        result = DiagnosisCRUD.create(diagnosis)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/diagnoses', methods=['GET'])
def get_diagnoses():
    """Get all diagnoses with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        diagnoses = DiagnosisCRUD.get_all(skip=skip, limit=limit)
        return jsonify([d.model_dump(mode='json') for d in diagnoses])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/diagnoses/<int:diagnosis_id>', methods=['GET'])
def get_diagnosis(diagnosis_id):
    """Get a specific diagnosis by ID"""
    diagnosis = DiagnosisCRUD.get(diagnosis_id)
    if not diagnosis:
        return jsonify({"error": "Diagnosis not found"}), 404
    return jsonify(diagnosis.model_dump(mode='json'))

@app.route('/diagnoses/search/<string:code>', methods=['GET'])
def search_diagnoses_by_code(code):
    """Search diagnoses by code"""
    diagnoses = DiagnosisCRUD.search_by_code(code)
    return jsonify([d.model_dump(mode='json') for d in diagnoses])

# ==================== PROCEDURE ROUTES ====================
@app.route('/procedures', methods=['POST'])
def create_procedure():
    """Create a new procedure"""
    try:
        data = request.get_json()
        procedure = ProcedureCreate(**data)
        result = ProcedureCRUD.create(procedure)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/procedures', methods=['GET'])
def get_procedures():
    """Get all procedures with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        procedures = ProcedureCRUD.get_all(skip=skip, limit=limit)
        return jsonify([p.model_dump(mode='json') for p in procedures])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/procedures/<int:procedure_id>', methods=['GET'])
def get_procedure(procedure_id):
    """Get a specific procedure by ID"""
    procedure = ProcedureCRUD.get(procedure_id)
    if not procedure:
        return jsonify({"error": "Procedure not found"}), 404
    return jsonify(procedure.model_dump(mode='json'))

# ==================== DRUG ROUTES ====================
@app.route('/drugs', methods=['POST'])
def create_drug():
    """Create a new drug"""
    try:
        data = request.get_json()
        drug = DrugCreate(**data)
        result = DrugCRUD.create(drug)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/drugs', methods=['GET'])
def get_drugs():
    """Get all drugs with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        drugs = DrugCRUD.get_all(skip=skip, limit=limit)
        return jsonify([d.model_dump(mode='json') for d in drugs])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/drugs/<int:drug_id>', methods=['GET'])
def get_drug(drug_id):
    """Get a specific drug by ID"""
    drug = DrugCRUD.get(drug_id)
    if not drug:
        return jsonify({"error": "Drug not found"}), 404
    return jsonify(drug.model_dump(mode='json'))

@app.route('/drugs/search/<string:name>', methods=['GET'])
def search_drugs_by_name(name):
    """Search drugs by brand name"""
    drugs = DrugCRUD.search_by_name(name)
    return jsonify([d.model_dump(mode='json') for d in drugs])

# ==================== PRESCRIPTION ROUTES ====================
@app.route('/prescriptions', methods=['POST'])
def create_prescription():
    """Create a new prescription"""
    try:
        data = request.get_json()
        prescription = PrescriptionCreate(**data)
        result = PrescriptionCRUD.create(prescription)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/prescriptions/<int:prescription_id>', methods=['GET'])
def get_prescription(prescription_id):
    """Get a specific prescription by ID"""
    prescription = PrescriptionCRUD.get(prescription_id)
    if not prescription:
        return jsonify({"error": "Prescription not found"}), 404
    return jsonify(prescription.model_dump(mode='json'))

@app.route('/prescriptions/visit/<int:visit_id>', methods=['GET'])
def get_prescriptions_by_visit(visit_id):
    """Get all prescriptions for a specific visit"""
    prescriptions = PrescriptionCRUD.get_by_visit(visit_id)
    return jsonify([p.model_dump(mode='json') for p in prescriptions])

@app.route('/prescriptions/all', methods=['GET'])
def get_all_prescriptions():
    """Get all prescriptions with basic patient and drug info for dropdown"""
    try:
        from clinic_api.services.reports import _sanitize_for_json
        
        db = Database.connect_db()
        
        # Get all prescriptions - get full documents to see what fields exist
        prescriptions = list(db.Prescription.find({}, {"_id": 0}).limit(10))
        
        # For debugging - print the first prescription to see field names
        if prescriptions:
            print("=" * 80)
            print(f"SAMPLE PRESCRIPTION FIELDS: {list(prescriptions[0].keys())}")
            print(f"SAMPLE PRESCRIPTION DATA: {prescriptions[0]}")
            print("=" * 80)
        
        result = []
        seen_ids = set()
        
        for rx in prescriptions:
            # Try all possible field name variations
            rx_id = (rx.get("Prescription_Id") or rx.get("prescription_id") or 
                    rx.get("PrescriptionId") or rx.get("prescriptionId"))
            
            if not rx_id or rx_id in seen_ids:
                continue
            seen_ids.add(rx_id)
            
            # Get IDs - prescriptions use capitalized field names
            visit_id = rx.get("Visit_Id")
            drug_id = rx.get("Drug_Id")
            
            # Get patient_id from visit - check BOTH capitalized and lowercase
            patient_id = None
            if visit_id:
                # Try both Visit_Id (capitalized) and visit_id (lowercase)
                visit = db.Visit.find_one(
                    {"$or": [{"Visit_Id": visit_id}, {"visit_id": visit_id}]},
                    {"_id": 0}
                )
                if visit:
                    # Visit might have Patient_Id (capitalized) OR patient_id (lowercase)
                    patient_id = visit.get("Patient_Id") or visit.get("patient_id")
            
            # Get patient name - Patient collection uses LOWERCASE field names
            patient_name = "Unknown Patient"
            if patient_id:
                # Patient uses lowercase: patient_id, first_name, last_name
                patient = db.Patient.find_one({"patient_id": patient_id}, {"_id": 0})
                if patient:
                    first = patient.get("first_name") or ""
                    last = patient.get("last_name") or ""
                    patient_name = f"{first} {last}".strip() or f"Patient {patient_id}"
            
            # Get drug name - Drug collection uses LOWERCASE field names
            drug_name = "Unknown Drug"
            if drug_id:
                # Drug uses lowercase: drug_id, brand_name, generic_name
                drug = db.Drug.find_one({"drug_id": drug_id}, {"_id": 0})
                if drug:
                    brand = drug.get("brand_name")
                    generic = drug.get("generic_name")
                    drug_name = brand or generic or f"Drug {drug_id}"
            
            # Get dosage
            dosage = (rx.get("Dosage_Instruction") or rx.get("dosage_instruction") or 
                     rx.get("DosageInstruction") or rx.get("Dosage") or rx.get("dosage") or "")
            
            # Get dispensed date
            dispensed_at = (rx.get("Dispensed_At") or rx.get("dispensed_at") or 
                           rx.get("DispensedAt") or rx.get("dispensedAt"))
            
            result.append({
                "prescription_id": rx_id,
                "patient_name": patient_name,
                "drug_name": drug_name,
                "dosage": dosage,
                "dispensed_at": dispensed_at
            })
        
        return jsonify(_sanitize_for_json(result))
    except Exception as e:
        logger.exception('Error fetching all prescriptions')
        return jsonify({"error": str(e)}), 500

@app.route('/prescriptions/<int:prescription_id>/details', methods=['GET'])
def get_prescription_details(prescription_id):
    """Get enriched prescription details with patient, drug, visit, and staff info"""
    try:
        from clinic_api.services.reports import _sanitize_for_json
        
        db = Database.connect_db()
        
        # Get prescription - try both field name variations
        prescription = db.Prescription.find_one({"prescription_id": prescription_id})
        if not prescription:
            prescription = db.Prescription.find_one({"Prescription_Id": prescription_id})
        if not prescription:
            return jsonify({"error": "Prescription not found"}), 404
        
        # Normalize field names (handle both lowercase and capitalized versions)
        def get_field(doc, field_name):
            if not doc:
                return None
            # Try lowercase with underscore
            if field_name in doc:
                return doc[field_name]
            # Try capitalized with underscore
            capitalized = field_name.replace('_', '_').title().replace('_', '_')
            if capitalized in doc:
                return doc[capitalized]
            # Try each word capitalized
            parts = field_name.split('_')
            cap_field = '_'.join([p.capitalize() for p in parts])
            if cap_field in doc:
                return doc[cap_field]
            return None
        
        # Extract IDs with field name tolerance
        visit_id = get_field(prescription, 'visit_id') or get_field(prescription, 'Visit_Id')
        drug_id = get_field(prescription, 'drug_id') or get_field(prescription, 'Drug_Id')
        patient_id = get_field(prescription, 'patient_id') or get_field(prescription, 'Patient_Id')
        dispensed_by_id = get_field(prescription, 'dispensed_by') or get_field(prescription, 'Dispensed_By')
        
        # Get related data
        patient = None
        if patient_id:
            patient = db.Patient.find_one({"patient_id": patient_id}) or db.Patient.find_one({"Patient_Id": patient_id})
        
        drug = None
        if drug_id:
            drug = db.Drug.find_one({"drug_id": drug_id}) or db.Drug.find_one({"Drug_Id": drug_id})
        
        visit = None
        if visit_id:
            visit = db.Visit.find_one({"visit_id": visit_id}) or db.Visit.find_one({"Visit_Id": visit_id})
        
        dispensed_by = None
        if dispensed_by_id:
            dispensed_by = db.Staff.find_one({"staff_id": dispensed_by_id}) or db.Staff.find_one({"Staff_Id": dispensed_by_id})
        
        # If we don't have a patient yet, try to get it from visit
        if not patient and visit:
            visit_patient_id = get_field(visit, 'patient_id') or get_field(visit, 'Patient_Id')
            if visit_patient_id:
                patient = db.Patient.find_one({"patient_id": visit_patient_id}) or db.Patient.find_one({"Patient_Id": visit_patient_id})
        
        result = {
            "prescription": _sanitize_for_json(prescription),
            "patient": _sanitize_for_json(patient),
            "drug": _sanitize_for_json(drug),
            "visit": _sanitize_for_json(visit),
            "dispensed_by": _sanitize_for_json(dispensed_by)
        }
        
        return jsonify(result)
    except Exception as e:
        logger.exception('Error fetching prescription details')
        return jsonify({"error": str(e)}), 500

# ==================== LAB TEST ORDER ROUTES ====================
@app.route('/lab-tests', methods=['POST'])
def create_lab_test():
    """Create a new lab test order"""
    try:
        data = request.get_json()
        lab_test = LabTestOrderCreate(**data)
        result = LabTestOrderCRUD.create(lab_test)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/lab-tests/<int:labtest_id>', methods=['GET'])
def get_lab_test(labtest_id):
    """Get a specific lab test by ID"""
    lab_test = LabTestOrderCRUD.get(labtest_id)
    if not lab_test:
        return jsonify({"error": "Lab test not found"}), 404
    return jsonify(lab_test.model_dump(mode='json'))

@app.route('/lab-tests/<int:labtest_id>', methods=['PUT'])
def update_lab_test(labtest_id):
    """Update a lab test order"""
    try:
        data = request.get_json()
        lab_test = LabTestOrderCreate(**data)
        updated_lab_test = LabTestOrderCRUD.update(labtest_id, lab_test)
        if not updated_lab_test:
            return jsonify({"error": "Lab test not found"}), 404
        return jsonify(updated_lab_test.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/lab-tests/<int:labtest_id>', methods=['DELETE'])
def delete_lab_test(labtest_id):
    """Delete a lab test order"""
    if not LabTestOrderCRUD.delete(labtest_id):
        return jsonify({"error": "Lab test not found"}), 404
    return '', 204

@app.route('/lab-tests/visit/<int:visit_id>', methods=['GET'])
def get_lab_tests_by_visit(visit_id):
    """Get all lab tests for a specific visit"""
    lab_tests = LabTestOrderCRUD.get_by_visit(visit_id)
    return jsonify([lt.model_dump(mode='json') for lt in lab_tests])


@app.route('/lab-tests/date/<date_str>', methods=['GET'])
def get_lab_tests_by_date(date_str):
    """Get lab tests (results) for a specific date (YYYY-MM-DD). Returns normalized dicts."""
    try:
        results = LabTestOrderCRUD.get_by_date(date_str)
        return jsonify(results)
    except Exception as e:
        logger.exception('Error fetching lab tests by date')
        return jsonify({'error': str(e)}), 500


@app.route('/lab-tests/today', methods=['GET'])
def get_lab_tests_today():
    """Convenience endpoint to fetch lab test results for today"""
    try:
        today = date.today().isoformat()
        results = LabTestOrderCRUD.get_by_date(today)
        return jsonify(results)
    except Exception as e:
        logger.exception('Error fetching today lab tests')
        return jsonify({'error': str(e)}), 500

# ==================== DELIVERY ROUTES ====================
@app.route('/deliveries', methods=['POST'])
def create_delivery():
    """Create a new delivery record"""
    try:
        data = request.get_json()
        delivery = DeliveryCreate(**data)
        result = DeliveryCRUD.create(delivery)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/deliveries/visit/<int:visit_id>', methods=['GET'])
def get_delivery_by_visit(visit_id):
    """Get delivery record by visit ID"""
    delivery = DeliveryCRUD.get_by_visit(visit_id)
    if not delivery:
        return jsonify({"error": "Delivery not found"}), 404
    return jsonify(delivery.model_dump(mode='json'))

@app.route('/deliveries/<int:delivery_id>', methods=['PUT'])
def update_delivery(delivery_id):
    """Update a delivery record"""
    try:
        data = request.get_json() or {}
        updated = DeliveryCRUD.update(delivery_id, data)
        if not updated:
            return jsonify({"error": "Delivery not found"}), 404
        return jsonify(updated.model_dump(mode='json'))
    except Exception as e:
        logger.exception('Error updating delivery')
        return jsonify({"error": str(e)}), 400

@app.route('/deliveries/<int:delivery_id>', methods=['DELETE'])
def delete_delivery(delivery_id):
    """Delete a delivery record"""
    try:
        ok = DeliveryCRUD.delete(delivery_id)
        if not ok:
            return jsonify({"error": "Delivery not found"}), 404
        return '', 204
    except Exception as e:
        logger.exception('Error deleting delivery')
        return jsonify({"error": str(e)}), 400


@app.route('/deliveries/date/<date_str>', methods=['GET'])
def get_deliveries_by_date(date_str):
    """Get delivery records for a specific date (YYYY-MM-DD)"""
    try:
        deliveries = DeliveryCRUD.get_by_date(date_str)
        # deliveries are returned as raw dicts from the service
        return jsonify(deliveries)
    except Exception as e:
        logger.exception('Error fetching deliveries by date')
        return jsonify({'error': str(e)}), 500


@app.route('/deliveries/today', methods=['GET'])
def get_deliveries_today():
    """Convenience endpoint to fetch today's deliveries"""
    try:
        today = date.today().isoformat()
        deliveries = DeliveryCRUD.get_by_date(today)
        return jsonify(deliveries)
    except Exception as e:
        logger.exception('Error fetching today deliveries')
        return jsonify({'error': str(e)}), 500

# ==================== RECOVERY STAY ROUTES ====================
@app.route('/recovery-stays', methods=['POST'])
def create_recovery_stay():
    """Create a new recovery stay"""
    try:
        data = request.get_json()
        recovery_stay = RecoveryStayCreate(**data)
        result = RecoveryStayCRUD.create(recovery_stay)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/recovery-stays/<int:stay_id>', methods=['GET'])
def get_recovery_stay(stay_id):
    """Get a specific recovery stay by ID"""
    stay = RecoveryStayCRUD.get(stay_id)
    if not stay:
        return jsonify({"error": "Recovery stay not found"}), 404
    return jsonify(stay.model_dump(mode='json'))


@app.route('/recovery-stays/<int:stay_id>', methods=['PUT'])
def update_recovery_stay(stay_id):
    """Update a recovery stay (e.g., set discharge time and discharged_by)"""
    try:
        data = request.get_json()
        # Only allow specific update fields for safety
        allowed = { 'discharge_time', 'discharged_by', 'notes' }
        updates = { k: v for k, v in (data or {}).items() if k in allowed }

        # Convert discharge_time to datetime if it's provided as ISO string
        if 'discharge_time' in updates and updates['discharge_time']:
            from datetime import datetime as _dt
            try:
                updates['discharge_time'] = _dt.fromisoformat(updates['discharge_time'])
            except Exception:
                # leave as-is, the service may accept string iso
                pass

        updated = RecoveryStayCRUD.update(stay_id, updates)
        if not updated:
            return jsonify({'error': 'Recovery stay not found'}), 404
        return jsonify(updated.model_dump(mode='json'))
    except Exception as e:
        logger.exception('Error updating recovery stay')
        return jsonify({'error': str(e)}), 400

@app.route('/recovery-stays/date/<date_str>', methods=['GET'])
def get_recovery_stays_by_date(date_str):
    """Get recovery stays for a given date (YYYY-MM-DD)."""
    try:
        stays = RecoveryStayCRUD.get_by_date(date_str)
        return jsonify(stays)
    except Exception as e:
        logger.exception('Error fetching recovery stays by date')
        return jsonify({'error': str(e)}), 500

@app.route('/recovery-stays/today', methods=['GET'])
def get_recovery_stays_today():
    """Convenience endpoint to fetch today's recovery stays."""
    try:
        today = date.today().isoformat()
        stays = RecoveryStayCRUD.get_by_date(today)
        return jsonify(stays)
    except Exception as e:
        logger.exception('Error fetching today recovery stays')
        return jsonify({'error': str(e)}), 500

@app.route('/recovery-stays/recent', methods=['GET'])
def get_recovery_stays_recent():
    """Get most recent recovery stays. Optional query param: limit (default 50)."""
    try:
        limit = request.args.get('limit', default=50, type=int)
        stays = RecoveryStayCRUD.get_recent(limit=limit)
        return jsonify(stays)
    except Exception as e:
        logger.exception('Error fetching recent recovery stays')
        return jsonify({'error': str(e)}), 500

# ==================== RECOVERY OBSERVATION ROUTES ====================
@app.route('/recovery-observations', methods=['POST'])
def create_recovery_observation():
    """Create a new recovery observation"""
    try:
        data = request.get_json()
        observation = RecoveryObservationCreate(**data)
        result = RecoveryObservationCRUD.create(observation)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/recovery-observations/stay/<int:stay_id>', methods=['GET'])
def get_recovery_observations_by_stay(stay_id):
    """Get all observations for a specific recovery stay"""
    observations = RecoveryObservationCRUD.get_by_stay(stay_id)
    return jsonify([o.model_dump(mode='json') for o in observations])

# ==================== INVOICE ROUTES ====================
@app.route('/invoices', methods=['POST'])
def create_invoice():
    """Create a new invoice"""
    try:
        data = request.get_json()
        invoice = InvoiceCreate(**data)
        result = InvoiceCRUD.create(invoice)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status')
        
        # Query MongoDB directly to avoid date serialization issues
        collection = Database.get_collection("Invoice")
        if status:
            invoices_data = list(collection.find({"Status": status}, {"_id": 0}).skip(skip).limit(limit))
        else:
            invoices_data = list(collection.find({}, {"_id": 0}).skip(skip).limit(limit))
        
        return jsonify(_sanitize_for_json(invoices_data))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get a specific invoice by ID"""
    invoice = InvoiceCRUD.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    return jsonify(invoice.model_dump(mode='json'))

@app.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    """Update an invoice"""
    try:
        data = request.get_json()
        invoice = InvoiceCreate(**data)
        updated_invoice = InvoiceCRUD.update(invoice_id, invoice)
        if not updated_invoice:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(updated_invoice.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/invoices/<int:invoice_id>/status', methods=['PUT'])
def update_invoice_status(invoice_id):
    """Update invoice status"""
    try:
        data = request.get_json()
        status = data.get('status')
        updated_invoice = InvoiceCRUD.update_status(invoice_id, status)
        if not updated_invoice:
            return jsonify({"error": "Invoice not found"}), 404
        return jsonify(updated_invoice.model_dump(mode='json'))
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    """Delete an invoice"""
    if not InvoiceCRUD.delete(invoice_id):
        return jsonify({"error": "Invoice not found"}), 404
    return '', 204

@app.route('/invoices/patient/<int:patient_id>', methods=['GET'])
def get_invoices_by_patient(patient_id):
    """Get all invoices for a specific patient"""
    invoices = InvoiceCRUD.get_by_patient(patient_id)
    return jsonify([i.model_dump(mode='json') for i in invoices])

# ==================== INVOICE LINE ROUTES ====================
@app.route('/invoices/<int:invoice_id>/lines', methods=['POST'])
def add_invoice_line(invoice_id):
    """Add a line item to an invoice"""
    try:
        data = request.get_json()
        data['invoice_id'] = invoice_id
        line = InvoiceLineCreate(**data)
        result = InvoiceLineCRUD.create(line)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/invoices/<int:invoice_id>/lines', methods=['GET'])
def get_invoice_lines(invoice_id):
    """Get all line items for a specific invoice"""
    lines = InvoiceLineCRUD.get_by_invoice(invoice_id)
    return jsonify([l.model_dump(mode='json') for l in lines])

@app.route('/invoices/<int:invoice_id>/lines/<int:line_no>', methods=['DELETE'])
def delete_invoice_line(invoice_id, line_no):
    """Remove a line item from an invoice"""
    if not InvoiceLineCRUD.delete(invoice_id, line_no):
        return jsonify({"error": "Invoice line not found"}), 404
    return '', 204

# ==================== PAYMENT ROUTES ====================
@app.route('/payments', methods=['POST'])
def create_payment():
    """Create a new payment"""
    try:
        data = request.get_json()
        payment = PaymentCreate(**data)
        result = PaymentCRUD.create(payment)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/payments', methods=['GET'])
def get_payments():
    """Get all payments with pagination"""
    try:
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 100, type=int)
        payments = PaymentCRUD.get_all(skip=skip, limit=limit)
        return jsonify([p.model_dump(mode='json') for p in payments])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Get a specific payment by ID"""
    payment = PaymentCRUD.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    return jsonify(payment.model_dump(mode='json'))

@app.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """Delete a payment"""
    if not PaymentCRUD.delete(payment_id):
        return jsonify({"error": "Payment not found"}), 404
    return '', 204

@app.route('/payments/patient/<int:patient_id>', methods=['GET'])
def get_payments_by_patient(patient_id):
    """Get all payments for a specific patient"""
    payments = PaymentCRUD.get_by_patient(patient_id)
    return jsonify([p.model_dump(mode='json') for p in payments])

@app.route('/invoices/<int:invoice_id>/payments', methods=['GET'])
def get_invoice_payments(invoice_id):
    """Get all payments for a specific invoice"""
    payments = PaymentCRUD.get_by_invoice(invoice_id)
    return jsonify([p.model_dump(mode='json') for p in payments])

@app.route('/payments/invoice/<int:invoice_id>', methods=['GET'])
def get_payments_by_invoice(invoice_id):
    """Get all payments for a specific invoice (legacy endpoint)"""
    payments = PaymentCRUD.get_by_invoice(invoice_id)
    return jsonify([p.model_dump(mode='json') for p in payments])

# ==================== WEEKLY COVERAGE (STAFF ASSIGNMENT) ROUTES ====================
@app.route('/staff_assignments', methods=['GET'])
def get_staff_assignments():
    """Fetches a sorted list of all current staff assignments"""
    try:
        assignments = StaffAssignmentCRUD.get_all()
        return jsonify({
            "status": "success",
            "assignments": [a.model_dump(mode='json') for a in assignments]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/staff_assignment', methods=['POST'])
def create_staff_assignment():
    """Adds a new staff assignment to the schedule"""
    try:
        data = request.get_json()
        assignment_in = StaffAssignmentCreate(**data)
        result = StaffAssignmentCRUD.create(assignment_in)
        
        return jsonify({
            "status": "success",
            "message": "Assignment added",
            "assignment": result.model_dump(mode='json')
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/staff_assignment/<int:assignment_id>', methods=['PUT'])
def update_staff_assignment(assignment_id):
    """Updates an existing assignment"""
    try:
        data = request.get_json()
        update_in = StaffAssignmentUpdate(**data)
        
        updated_assignment = StaffAssignmentCRUD.update(assignment_id, update_in)
        
        if not updated_assignment:
            return jsonify({
                "status": "error", 
                "message": f"Assignment with id {assignment_id} not found"
            }), 404
            
        return jsonify({
            "status": "success",
            "message": "Assignment updated",
            "assignment": updated_assignment.model_dump(mode='json')
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/staff_assignment/<int:assignment_id>', methods=['DELETE'])
def delete_staff_assignment(assignment_id):
    """Deletes an existing assignment"""
    try:
        success = StaffAssignmentCRUD.delete(assignment_id)
        if not success:
            return jsonify({
                "status": "error", 
                "message": f"Assignment with id {assignment_id} not found"
            }), 404 # Note: Prompt example implies success response format even on failure, but standard API practice is 404. 
                    # If you strictly want 200 OK with error message, remove the , 404.
            
        return jsonify({
            "status": "success",
            "message": f"Assignment with id {assignment_id} deleted"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==================== REPORT ROUTES (VIEWS & STORED PROCS) ====================
@app.route('/reports/monthly-activity', methods=['GET'])
def get_monthly_report():
    """Generates the Monthly Activity Report"""
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    if not month or not year:
        return jsonify({"error": "Month and Year required"}), 400
        
    report = ReportService.get_monthly_activity_report(month, year)
    return jsonify(report)

@app.route('/reports/outstanding-balances', methods=['GET'])
def get_outstanding_balances():
    """Patient Monthly Statement view for unpaid accounts"""
    balances = ReportService.get_outstanding_balances()
    return jsonify(balances)


@app.route('/statements/monthly', methods=['GET'])
def get_monthly_statements():
    """Get patient monthly statements split into paid/unpaid by invoice date."""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        if not month or not year:
            return jsonify({"error": "Month and Year required"}), 400

        results = ReportService.get_monthly_statements(month, year)
        # Final safety: sanitize any remaining BSON types before jsonify
        try:
            results = _sanitize_for_json(results)
        except Exception:
            logger.exception('Failed to sanitize monthly statements result')
        return jsonify(results)
    except Exception as e:
        # Log full stack for server-side debugging and return safe error info
        logger.exception('Error in /statements/monthly')
        tb = traceback.format_exc()
        return jsonify({"error": "internal server error", "detail": str(e), "trace": tb}), 500


@app.route('/debug/routes', methods=['GET'])
def list_routes():
    """Debug endpoint: list registered routes (for dev only)."""
    try:
        rules = []
        for rule in app.url_map.iter_rules():
            rules.append({
                'endpoint': rule.endpoint,
                'methods': sorted([m for m in rule.methods if m not in ('HEAD','OPTIONS')]),
                'rule': str(rule)
            })
        return jsonify({'routes': rules}), 200
    except Exception:
        logger.exception('Failed to list routes')
        return jsonify({'error': 'failed to list routes'}), 500

@app.route('/reports/daily-delivery-log', methods=['GET'])
def get_delivery_log():
    """Daily Delivery Log View"""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date required"}), 400
    
    log_date = date.fromisoformat(date_str)
    log = ReportService.get_daily_delivery_log(log_date)
    return jsonify(log)

# ==================== INSURER ROUTES ====================
@app.route('/insurers', methods=['POST'])
def create_insurer():
    try:
        data = request.get_json()
        insurer = InsurerCreate(**data)
        result = InsurerCRUD.create(insurer)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/insurers', methods=['GET'])
def get_insurers():
    insurers = InsurerCRUD.get_all()
    return jsonify([i.model_dump(mode='json') for i in insurers])

# ==================== STAFF SHIFT ROUTES (MASTER SCHEDULE) ====================
@app.route('/schedules/shifts', methods=['POST'])
def create_staff_shift():
    try:
        data = request.get_json()
        shift = StaffShiftCreate(**data)
        result = StaffShiftCRUD.create(shift)
        return jsonify(result.model_dump(mode='json')), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/schedules/shifts/<int:shift_id>', methods=['DELETE'])
def delete_staff_shift(shift_id):
    """Delete a staff shift"""
    try:
        if not StaffShiftCRUD.delete(shift_id):
            return jsonify({"error": "Staff shift not found"}), 404
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/schedules/daily-master', methods=['GET'])
def get_daily_master_schedule():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"error": "Date required"}), 400
    
    target_date = date.fromisoformat(date_str)
    shifts = StaffShiftCRUD.get_daily_master_schedule(target_date)
    return jsonify([s.model_dump(mode='json') for s in shifts])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)