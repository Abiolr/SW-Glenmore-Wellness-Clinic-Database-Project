from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date, timedelta
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
# ============================================================================
# ENDPOINT 1: Visit Complete Details
# ============================================================================

@app.route('/api/views/visit-details', methods=['GET'])
def get_visit_complete_details():
    """
    Get complete visit details with patient, staff, prescriptions, and lab tests
    
    Query Parameters:
    - status: Filter by visit status ("Active" or "Completed")
    - patient_id: Filter by patient ID
    - staff_id: Filter by staff ID
    - start_date: Filter visits from this date (ISO format)
    - end_date: Filter visits until this date (ISO format)
    - limit: Limit number of results (default: 100)
    
    Examples:
    - GET /api/views/visit-details
    - GET /api/views/visit-details?status=Active
    - GET /api/views/visit-details?patient_id=43
    - GET /api/views/visit-details?staff_id=48&limit=10
    - GET /api/views/visit-details?start_date=2025-11-01&end_date=2025-11-30
    
    Response:
    {
        "data": [
            {
                "visit_id": 2,
                "patient_name": "John Doe",
                "staff_name": "Dr. Smith",
                "visit_status": "Active",
                "prescription_count": 2,
                "lab_test_count": 1,
                ...
            }
        ],
        "count": 10,
        "filters_applied": {...}
    }
    """
    try:
        db = Database.connect_db()
        
        # Build filter query
        filter_query = {}
        
        # Filter by status
        status = request.args.get('status')
        if status:
            filter_query['visit_status'] = status
        
        # Filter by patient
        patient_id = request.args.get('patient_id')
        if patient_id:
            try:
                filter_query['patient_id'] = int(patient_id)
            except ValueError:
                return jsonify({'error': 'Invalid patient_id'}), 400
        
        # Filter by staff
        staff_id = request.args.get('staff_id')
        if staff_id:
            try:
                filter_query['staff_id'] = int(staff_id)
            except ValueError:
                return jsonify({'error': 'Invalid staff_id'}), 400
        
        # Filter by date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    date_filter['$gte'] = datetime.fromisoformat(start_date)
                except ValueError:
                    return jsonify({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'}), 400
            
            if end_date:
                try:
                    # Add one day to include the entire end_date
                    end_datetime = datetime.fromisoformat(end_date) + timedelta(days=1)
                    date_filter['$lt'] = end_datetime
                except ValueError:
                    return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'}), 400
            
            filter_query['start_time'] = date_filter
        
        # Get limit
        limit = request.args.get('limit', 100)
        try:
            limit = int(limit)
            if limit > 1000:
                limit = 1000  # Max limit
        except ValueError:
            limit = 100
        
        # Query the view
        visits = list(db.visit_complete_details.find(filter_query, {'_id': 0}).limit(limit))
        count = len(visits)
        
        return jsonify({
            'data': visits,
            'count': count,
            'filters_applied': {
                'status': status,
                'patient_id': patient_id,
                'staff_id': staff_id,
                'start_date': start_date,
                'end_date': end_date,
                'limit': limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ENDPOINT 2: Patient Financial Summary
# ============================================================================

@app.route('/api/views/patient-financials', methods=['GET'])
def get_patient_financial_summary():
    """
    Get patient financial summary with invoices and payments
    
    Query Parameters:
    - patient_id: Filter by patient ID
    - has_balance: Filter patients with outstanding balance (true/false)
    - min_balance: Minimum outstanding balance
    - sort_by: Sort field (outstanding_balance, total_invoiced, total_paid)
    - sort_order: Sort order (asc, desc) - default: desc
    - limit: Limit number of results (default: 100)
    
    Examples:
    - GET /api/views/patient-financials
    - GET /api/views/patient-financials?has_balance=true
    - GET /api/views/patient-financials?min_balance=100
    - GET /api/views/patient-financials?sort_by=outstanding_balance&sort_order=desc
    - GET /api/views/patient-financials?patient_id=30
    
    Response:
    {
        "data": [
            {
                "patient_id": 30,
                "full_name": "John Doe",
                "total_invoiced": 500.00,
                "total_paid": 300.00,
                "outstanding_balance": 200.00,
                "has_outstanding_balance": true,
                ...
            }
        ],
        "count": 15,
        "summary": {
            "total_outstanding": 5000.00,
            "total_invoiced": 10000.00,
            "total_paid": 5000.00
        }
    }
    """
    try:
        db = Database.connect_db()
        
        # Build filter query
        filter_query = {}
        
        # Filter by patient
        patient_id = request.args.get('patient_id')
        if patient_id:
            try:
                filter_query['patient_id'] = int(patient_id)
            except ValueError:
                return jsonify({'error': 'Invalid patient_id'}), 400
        
        # Filter by outstanding balance
        has_balance = request.args.get('has_balance')
        if has_balance:
            if has_balance.lower() == 'true':
                filter_query['has_outstanding_balance'] = True
            elif has_balance.lower() == 'false':
                filter_query['has_outstanding_balance'] = False
        
        # Filter by minimum balance
        min_balance = request.args.get('min_balance')
        if min_balance:
            try:
                filter_query['outstanding_balance'] = {'$gte': float(min_balance)}
            except ValueError:
                return jsonify({'error': 'Invalid min_balance'}), 400
        
        # Get sort parameters
        sort_by = request.args.get('sort_by', 'outstanding_balance')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort_by field
        valid_sort_fields = ['outstanding_balance', 'total_invoiced', 'total_paid', 'patient_id', 'full_name']
        if sort_by not in valid_sort_fields:
            sort_by = 'outstanding_balance'
        
        # Convert sort order
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Get limit
        limit = request.args.get('limit', 100)
        try:
            limit = int(limit)
            if limit > 1000:
                limit = 1000
        except ValueError:
            limit = 100
        
        # Query the view
        patients = list(db.patient_financial_summary.find(
            filter_query, 
            {'_id': 0}
        ).sort(sort_by, sort_direction).limit(limit))
        
        count = len(patients)
        
        # Calculate summary statistics
        summary = {
            'total_outstanding': sum(p.get('outstanding_balance', 0) for p in patients),
            'total_invoiced': sum(p.get('total_invoiced', 0) for p in patients),
            'total_paid': sum(p.get('total_paid', 0) for p in patients),
            'patients_with_balance': sum(1 for p in patients if p.get('has_outstanding_balance', False))
        }
        
        return jsonify({
            'data': patients,
            'count': count,
            'summary': summary,
            'filters_applied': {
                'patient_id': patient_id,
                'has_balance': has_balance,
                'min_balance': min_balance,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ENDPOINT 3: Staff Workload Analysis
# ============================================================================

@app.route('/api/views/staff-workload', methods=['GET'])
def get_staff_workload_analysis():
    """
    Get staff workload analysis with appointments, visits, and performance metrics
    
    Query Parameters:
    - staff_id: Filter by staff ID
    - active_only: Show only active staff (true/false) - default: true
    - is_busy: Filter staff with active visits (true/false)
    - min_workload: Minimum workload score
    - sort_by: Sort field (workload_score, total_visits, total_appointments)
    - sort_order: Sort order (asc, desc) - default: desc
    
    Examples:
    - GET /api/views/staff-workload
    - GET /api/views/staff-workload?is_busy=true
    - GET /api/views/staff-workload?min_workload=10
    - GET /api/views/staff-workload?staff_id=48
    - GET /api/views/staff-workload?sort_by=workload_score
    
    Response:
    {
        "data": [
            {
                "staff_id": 48,
                "full_name": "Dr. Jane Smith",
                "total_appointments": 15,
                "active_visits": 2,
                "workload_score": 35,
                "is_busy": true,
                ...
            }
        ],
        "count": 5,
        "summary": {
            "total_staff": 5,
            "busy_staff": 2,
            "total_active_visits": 5
        }
    }
    """
    try:
        db = Database.connect_db()
        
        # Build filter query
        filter_query = {}
        
        # Filter by staff ID
        staff_id = request.args.get('staff_id')
        if staff_id:
            try:
                filter_query['staff_id'] = int(staff_id)
            except ValueError:
                return jsonify({'error': 'Invalid staff_id'}), 400
        
        # Filter by active status
        active_only = request.args.get('active_only', 'true')
        if active_only.lower() == 'true':
            filter_query['active'] = True
        
        # Filter by busy status
        is_busy = request.args.get('is_busy')
        if is_busy:
            if is_busy.lower() == 'true':
                filter_query['is_busy'] = True
            elif is_busy.lower() == 'false':
                filter_query['is_busy'] = False
        
        # Filter by minimum workload
        min_workload = request.args.get('min_workload')
        if min_workload:
            try:
                filter_query['workload_score'] = {'$gte': float(min_workload)}
            except ValueError:
                return jsonify({'error': 'Invalid min_workload'}), 400
        
        # Get sort parameters
        sort_by = request.args.get('sort_by', 'workload_score')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort_by field
        valid_sort_fields = ['workload_score', 'total_visits', 'total_appointments', 'active_visits', 'staff_id']
        if sort_by not in valid_sort_fields:
            sort_by = 'workload_score'
        
        # Convert sort order
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Query the view
        staff = list(db.staff_workload_analysis.find(
            filter_query,
            {'_id': 0}
        ).sort(sort_by, sort_direction))
        
        count = len(staff)
        
        # Calculate summary statistics
        summary = {
            'total_staff': count,
            'busy_staff': sum(1 for s in staff if s.get('is_busy', False)),
            'total_active_visits': sum(s.get('active_visits', 0) for s in staff),
            'total_appointments': sum(s.get('total_appointments', 0) for s in staff),
            'avg_workload_score': sum(s.get('workload_score', 0) for s in staff) / count if count > 0 else 0
        }
        
        return jsonify({
            'data': staff,
            'count': count,
            'summary': summary,
            'filters_applied': {
                'staff_id': staff_id,
                'active_only': active_only,
                'is_busy': is_busy,
                'min_workload': min_workload,
                'sort_by': sort_by
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ENDPOINT 4: Daily Clinic Schedule
# ============================================================================

@app.route('/api/views/clinic-schedule', methods=['GET'])
def get_daily_clinic_schedule():
    """
    Get daily clinic schedule with appointments
    
    Query Parameters:
    - date: Filter by specific date (YYYY-MM-DD) - default: today
    - staff_id: Filter by staff ID
    - patient_id: Filter by patient ID
    - appointment_type: Filter by type ("Walk-in" or "Scheduled")
    - start_time: Filter appointments from this time
    - end_time: Filter appointments until this time
    
    Examples:
    - GET /api/views/clinic-schedule
    - GET /api/views/clinic-schedule?date=2025-11-25
    - GET /api/views/clinic-schedule?staff_id=65
    - GET /api/views/clinic-schedule?appointment_type=Walk-in
    - GET /api/views/clinic-schedule?start_time=2025-11-25T09:00:00&end_time=2025-11-25T17:00:00
    
    Response:
    {
        "data": [
            {
                "appointment_id": 37,
                "patient_name": "John Doe",
                "staff_name": "Dr. Smith",
                "scheduled_start": "2025-11-20T10:00:00",
                "appointment_type": "Scheduled",
                "color": "#4285f4",
                ...
            }
        ],
        "count": 12,
        "date": "2025-11-25",
        "summary": {
            "total_appointments": 12,
            "walk_ins": 3,
            "scheduled": 9
        }
    }
    """
    try:
        db = Database.connect_db()
        
        # Build filter query
        filter_query = {}
        
        # Filter by date (default to today)
        date_param = request.args.get('date')
        if date_param:
            try:
                filter_date = datetime.fromisoformat(date_param)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            filter_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Set date range for the entire day
        start_of_day = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Apply date filter
        filter_query['scheduled_start'] = {
            '$gte': start_of_day,
            '$lt': end_of_day
        }
        
        # Filter by staff
        staff_id = request.args.get('staff_id')
        if staff_id:
            try:
                filter_query['staff_id'] = int(staff_id)
            except ValueError:
                return jsonify({'error': 'Invalid staff_id'}), 400
        
        # Filter by patient
        patient_id = request.args.get('patient_id')
        if patient_id:
            try:
                filter_query['patient_id'] = int(patient_id)
            except ValueError:
                return jsonify({'error': 'Invalid patient_id'}), 400
        
        # Filter by appointment type
        appointment_type = request.args.get('appointment_type')
        if appointment_type:
            filter_query['appointment_type'] = appointment_type
        
        # Custom time range (overrides date filter if provided)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time or end_time:
            time_filter = {}
            if start_time:
                try:
                    time_filter['$gte'] = datetime.fromisoformat(start_time)
                except ValueError:
                    return jsonify({'error': 'Invalid start_time format'}), 400
            
            if end_time:
                try:
                    time_filter['$lt'] = datetime.fromisoformat(end_time)
                except ValueError:
                    return jsonify({'error': 'Invalid end_time format'}), 400
            
            filter_query['scheduled_start'] = time_filter
        
        # Query the view
        appointments = list(db.daily_clinic_schedule.find(
            filter_query,
            {'_id': 0}
        ).sort('scheduled_start', 1))
        
        count = len(appointments)
        
        # Calculate summary
        summary = {
            'total_appointments': count,
            'walk_ins': sum(1 for a in appointments if a.get('appointment_type') == 'Walk-in'),
            'scheduled': sum(1 for a in appointments if a.get('appointment_type') == 'Scheduled'),
            'unique_patients': len(set(a.get('patient_id') for a in appointments if a.get('patient_id'))),
            'unique_staff': len(set(a.get('staff_id') for a in appointments if a.get('staff_id')))
        }
        
        return jsonify({
            'data': appointments,
            'count': count,
            'date': filter_date.date().isoformat(),
            'summary': summary,
            'filters_applied': {
                'date': date_param or 'today',
                'staff_id': staff_id,
                'patient_id': patient_id,
                'appointment_type': appointment_type
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ENDPOINT 5: Patient Clinical History
# ============================================================================

@app.route('/api/views/patient-history', methods=['GET'])
def get_patient_clinical_history():
    """
    Get patient clinical history with visits and financial summary
    
    Query Parameters:
    - patient_id: Filter by patient ID (required if not using other filters)
    - has_active_visit: Filter patients with active visits (true/false)
    - needs_follow_up: Filter patients needing follow-up (true/false)
    - min_visits: Minimum number of visits
    - has_balance: Filter patients with outstanding balance (true/false)
    - sort_by: Sort field (last_visit_date, total_visits, outstanding_balance)
    - sort_order: Sort order (asc, desc) - default: desc
    - limit: Limit number of results (default: 100)
    
    Examples:
    - GET /api/views/patient-history?patient_id=30
    - GET /api/views/patient-history?has_active_visit=true
    - GET /api/views/patient-history?needs_follow_up=true
    - GET /api/views/patient-history?min_visits=5
    - GET /api/views/patient-history?has_balance=true&sort_by=outstanding_balance
    
    Response:
    {
        "data": [
            {
                "patient_id": 30,
                "full_name": "John Doe",
                "total_visits": 12,
                "active_visits": 1,
                "outstanding_balance": 200.00,
                "needs_follow_up": true,
                ...
            }
        ],
        "count": 25,
        "summary": {
            "total_patients": 25,
            "with_active_visits": 5,
            "needing_follow_up": 8
        }
    }
    """
    try:
        db = Database.connect_db()
        
        # Build filter query
        filter_query = {}
        
        # Filter by patient ID
        patient_id = request.args.get('patient_id')
        if patient_id:
            try:
                filter_query['patient_id'] = int(patient_id)
            except ValueError:
                return jsonify({'error': 'Invalid patient_id'}), 400
        
        # Filter by active visit
        has_active_visit = request.args.get('has_active_visit')
        if has_active_visit:
            if has_active_visit.lower() == 'true':
                filter_query['has_active_visit'] = True
            elif has_active_visit.lower() == 'false':
                filter_query['has_active_visit'] = False
        
        # Filter by follow-up needed
        needs_follow_up = request.args.get('needs_follow_up')
        if needs_follow_up:
            if needs_follow_up.lower() == 'true':
                filter_query['needs_follow_up'] = True
            elif needs_follow_up.lower() == 'false':
                filter_query['needs_follow_up'] = False
        
        # Filter by minimum visits
        min_visits = request.args.get('min_visits')
        if min_visits:
            try:
                filter_query['total_visits'] = {'$gte': int(min_visits)}
            except ValueError:
                return jsonify({'error': 'Invalid min_visits'}), 400
        
        # Filter by outstanding balance
        has_balance = request.args.get('has_balance')
        if has_balance:
            if has_balance.lower() == 'true':
                filter_query['has_outstanding_balance'] = True
            elif has_balance.lower() == 'false':
                filter_query['has_outstanding_balance'] = False
        
        # Get sort parameters
        sort_by = request.args.get('sort_by', 'last_visit_date')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Validate sort_by field
        valid_sort_fields = ['last_visit_date', 'total_visits', 'outstanding_balance', 'patient_id', 'full_name']
        if sort_by not in valid_sort_fields:
            sort_by = 'last_visit_date'
        
        # Convert sort order
        sort_direction = -1 if sort_order == 'desc' else 1
        
        # Get limit
        limit = request.args.get('limit', 100)
        try:
            limit = int(limit)
            if limit > 1000:
                limit = 1000
        except ValueError:
            limit = 100
        
        # Query the view
        patients = list(db.patient_clinical_history.find(
            filter_query,
            {'_id': 0}
        ).sort(sort_by, sort_direction).limit(limit))
        
        count = len(patients)
        
        # Calculate summary
        summary = {
            'total_patients': count,
            'with_active_visits': sum(1 for p in patients if p.get('has_active_visit', False)),
            'needing_follow_up': sum(1 for p in patients if p.get('needs_follow_up', False)),
            'with_outstanding_balance': sum(1 for p in patients if p.get('has_outstanding_balance', False)),
            'total_visits': sum(p.get('total_visits', 0) for p in patients),
            'total_outstanding': sum(p.get('outstanding_balance', 0) for p in patients)
        }
        
        return jsonify({
            'data': patients,
            'count': count,
            'summary': summary,
            'filters_applied': {
                'patient_id': patient_id,
                'has_active_visit': has_active_visit,
                'needs_follow_up': needs_follow_up,
                'min_visits': min_visits,
                'has_balance': has_balance,
                'sort_by': sort_by
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# BONUS: Views Summary Endpoint
# ============================================================================

@app.route('/api/views/summary', methods=['GET'])
def get_views_summary():
    """
    Get summary statistics from all views
    
    Provides a quick overview of:
    - Total visits (active vs completed)
    - Total patients (with balances, needing follow-up)
    - Total staff (busy vs available)
    - Today's appointments
    - Overall financials
    
    Example:
    - GET /api/views/summary
    
    Response:
    {
        "visits": {
            "total": 50,
            "active": 5,
            "completed": 45
        },
        "patients": {
            "total": 100,
            "with_balance": 25,
            "needing_follow_up": 15
        },
        "staff": {
            "total": 10,
            "active": 8,
            "busy": 3
        },
        "appointments": {
            "today": 20,
            "walk_ins": 5,
            "scheduled": 15
        },
        "financials": {
            "total_outstanding": 5000.00,
            "total_invoiced": 50000.00,
            "total_paid": 45000.00
        }
    }
    """
    try:
        db = Database.connect_db()
        
        # Get visit summary
        visits_stats = list(db.visit_complete_details.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'active': {
                        '$sum': {
                            '$cond': [{'$eq': ['$visit_status', 'Active']}, 1, 0]
                        }
                    }
                }
            }
        ]))
        
        visits_summary = {
            'total': visits_stats[0]['total'] if visits_stats else 0,
            'active': visits_stats[0]['active'] if visits_stats else 0,
            'completed': (visits_stats[0]['total'] - visits_stats[0]['active']) if visits_stats else 0
        }
        
        # Get patient summary
        patients_stats = list(db.patient_clinical_history.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'with_balance': {
                        '$sum': {
                            '$cond': ['$has_outstanding_balance', 1, 0]
                        }
                    },
                    'needing_follow_up': {
                        '$sum': {
                            '$cond': ['$needs_follow_up', 1, 0]
                        }
                    }
                }
            }
        ]))
        
        patients_summary = {
            'total': patients_stats[0]['total'] if patients_stats else 0,
            'with_balance': patients_stats[0]['with_balance'] if patients_stats else 0,
            'needing_follow_up': patients_stats[0]['needing_follow_up'] if patients_stats else 0
        }
        
        # Get staff summary
        staff_stats = list(db.staff_workload_analysis.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'active': {
                        '$sum': {
                            '$cond': ['$active', 1, 0]
                        }
                    },
                    'busy': {
                        '$sum': {
                            '$cond': ['$is_busy', 1, 0]
                        }
                    }
                }
            }
        ]))
        
        staff_summary = {
            'total': staff_stats[0]['total'] if staff_stats else 0,
            'active': staff_stats[0]['active'] if staff_stats else 0,
            'busy': staff_stats[0]['busy'] if staff_stats else 0
        }
        
        # Get today's appointments
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        appointments_stats = list(db.daily_clinic_schedule.aggregate([
            {
                '$match': {
                    'scheduled_start': {
                        '$gte': today_start,
                        '$lt': today_end
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total': {'$sum': 1},
                    'walk_ins': {
                        '$sum': {
                            '$cond': [{'$eq': ['$appointment_type', 'Walk-in']}, 1, 0]
                        }
                    }
                }
            }
        ]))
        
        appointments_summary = {
            'today': appointments_stats[0]['total'] if appointments_stats else 0,
            'walk_ins': appointments_stats[0]['walk_ins'] if appointments_stats else 0,
            'scheduled': (appointments_stats[0]['total'] - appointments_stats[0]['walk_ins']) if appointments_stats else 0
        }
        
        # Get financial summary
        financials_stats = list(db.patient_financial_summary.aggregate([
            {
                '$group': {
                    '_id': None,
                    'total_outstanding': {'$sum': '$outstanding_balance'},
                    'total_invoiced': {'$sum': '$total_invoiced'},
                    'total_paid': {'$sum': '$total_paid'}
                }
            }
        ]))
        
        financials_summary = {
            'total_outstanding': financials_stats[0]['total_outstanding'] if financials_stats else 0,
            'total_invoiced': financials_stats[0]['total_invoiced'] if financials_stats else 0,
            'total_paid': financials_stats[0]['total_paid'] if financials_stats else 0
        }
        
        return jsonify({
            'visits': visits_summary,
            'patients': patients_summary,
            'staff': staff_summary,
            'appointments': appointments_summary,
            'financials': financials_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
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
        
        # Get all prescriptions and manually join with patient/drug data
        prescriptions = list(db.Prescription.find({}, {"_id": 0}).sort("Prescription_Id", -1).limit(100))
        
        result = []
        seen_ids = set()
        
        for rx in prescriptions:
            rx_id = rx.get("Prescription_Id") or rx.get("prescription_id")
            
            # Skip duplicates
            if rx_id in seen_ids:
                continue
            seen_ids.add(rx_id)
            
            patient_id = rx.get("Patient_Id") or rx.get("patient_id")
            drug_id = rx.get("Drug_Id") or rx.get("drug_id")
            
            # Get patient name
            patient_name = "Unknown Patient"
            if patient_id:
                patient = db.Patient.find_one(
                    {"$or": [{"Patient_Id": patient_id}, {"patient_id": patient_id}]},
                    {"First_Name": 1, "Last_Name": 1, "first_name": 1, "last_name": 1, "_id": 0}
                )
                if patient:
                    first = patient.get("First_Name") or patient.get("first_name") or ""
                    last = patient.get("Last_Name") or patient.get("last_name") or ""
                    patient_name = f"{first} {last}".strip()
            
            # Get drug name
            drug_name = "Unknown Drug"
            if drug_id:
                drug = db.Drug.find_one(
                    {"$or": [{"Drug_Id": drug_id}, {"drug_id": drug_id}]},
                    {"Brand_Name": 1, "brand_name": 1, "_id": 0}
                )
                if drug:
                    drug_name = drug.get("Brand_Name") or drug.get("brand_name") or "Unknown Drug"
            
            result.append({
                "prescription_id": rx_id,
                "patient_name": patient_name,
                "drug_name": drug_name,
                "dosage": rx.get("Dosage_Instruction") or rx.get("dosage") or rx.get("Dosage") or "",
                "dispensed_at": rx.get("Dispensed_At") or rx.get("dispensed_at")
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
        
        if status:
            invoices = InvoiceCRUD.get_by_status(status)
        else:
            invoices = InvoiceCRUD.get_all(skip=skip, limit=limit)
        
        return jsonify([i.model_dump(mode='json') for i in invoices])
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

@app.route('/payments/invoice/<int:invoice_id>', methods=['GET'])
def get_payments_by_invoice(invoice_id):
    """Get all payments for a specific invoice"""
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