# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from connection_DB import db
from services.weekly_coverage import *
from services.appointment import *
from services.staff import *
from services.patient import *

load_dotenv()

app = Flask(__name__)
CORS(app)

def test_db_connection():
    """Test if database is actually reachable using the imported db object"""
    if db is None:
        return "disconnected: db object is None (check connection_DB.py)"
    try:
        db.client.admin.command('ping')
        return "connected"
    except Exception as e:
        return f"disconnected: {str(e)}"

@app.route('/')
def home():
    """Health check endpoint."""
    db_status = test_db_connection()
    return jsonify({
        "api_status": "ok",
        "db_status": db_status,
        "service": "SW Glenmore Wellness Clinic",
        "version": "1.0"
    })

"""
=========================
WEEKLY COVERAGE ENDPOINTS
=========================
"""
@app.route('/staff_assignments', methods=['GET'])
def get_staff_assignments():
    """
    Lists all staff assignments. Logic is handled in weekly_coverage.py.
    """
    try:
        response, status_code = handle_get_staff_assignments(db)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff_assignment', methods=['POST'])
def add_staff_assignment():
    """
    Adds a new staff assignment. Logic is handled in weekly_coverage.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_add_staff_assignment(db, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff_assignment/<int:assignment_id>', methods=['PUT'])
def update_staff_assignment(assignment_id):
    """
    Updates an existing assignment. Logic is handled in weekly_coverage.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_update_staff_assignment(db, assignment_id, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff_assignment/<int:assignment_id>', methods=['DELETE'])
def delete_staff_assignment(assignment_id):
    """
    Deletes an existing assignment. Logic is handled in weekly_coverage.py.
    """
    try:
        response, status_code = handle_delete_staff_assignment(db, assignment_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

"""
=================
STAFF ENDPOINTS
=================
"""
@app.route('/staff', methods=['GET'])
def get_all_staff():
    """
    Lists all staff members. Logic is handled in staff.py.
    """
    try:
        response, status_code = handle_get_all_staff(db)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff/<int:staff_id>', methods=['GET'])
def get_staff_by_id(staff_id):
    """
    Gets a single staff member by ID. Logic is handled in staff.py.
    """
    try:
        response, status_code = handle_get_staff_by_id(db, staff_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff', methods=['POST'])
def add_staff():
    """
    Adds a new staff member. Logic is handled in staff.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_add_staff(db, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """
    Updates an existing staff member. Logic is handled in staff.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_update_staff(db, staff_id, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """
    Deletes an existing staff member. Logic is handled in staff.py.
    """
    try:
        response, status_code = handle_delete_staff(db, staff_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

"""
===================
PATIENT ENDPOINTS
===================
"""
@app.route('/patients', methods=['GET'])
def get_all_patients():
    """
    Lists all patients. Logic is handled in patient.py.
    """
    try:
        response, status_code = handle_get_all_patients(db)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_by_id(patient_id):
    """
    Gets a single patient by ID. Logic is handled in patient.py.
    """
    try:
        response, status_code = handle_get_patient_by_id(db, patient_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/patient', methods=['POST'])
def add_patient():
    """
    Adds a new patient. Logic is handled in patient.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_add_patient(db, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/patient/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """
    Updates an existing patient. Logic is handled in patient.py.
    """
    try:
        data = request.get_json()
        response, status_code = handle_update_patient(db, patient_id, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """
    Deletes an existing patient. Logic is handled in patient.py.
    """
    try:
        response, status_code = handle_delete_patient(db, patient_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

"""
================================
APPOINTMENT SCHEDULE ENDPOINTS
================================
"""

@app.route('/schedule/master', methods=['GET'])
def get_master_schedule():
    """
    Fetches the master schedule for a given date.
    Query Params: ?date=YYYY-MM-DD
    """
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({"status": "error", "message": "Missing required query parameter: date"}), 400
        
        response, status_code = handle_get_master_schedule(db, date)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/schedule/practitioner', methods=['GET'])
def get_practitioner_schedule():
    """
    Fetches a single practitioner's schedule for a given date.
    Query Params: ?date=YYYY-MM-DD&practitioner_name=Name
    """
    try:
        date = request.args.get('date')
        practitioner_name = request.args.get('practitioner_name')
        
        if not date or not practitioner_name:
            return jsonify({"status": "error", "message": "Missing required query parameters: date and/or practitioner_name"}), 400
        
        response, status_code = handle_get_practitioner_schedule(db, date, practitioner_name)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/schedule/appointment', methods=['POST'])
def add_appointment():
    """
    Adds a new pre-scheduled appointment.
    """
    try:
        data = request.get_json()
        response, status_code = handle_add_appointment(db, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/schedule/walk_in', methods=['POST'])
def add_walk_in():
    """
    Adds a new walk-in patient to the schedule.
    """
    try:
        data = request.get_json()
        response, status_code = handle_add_walk_in(db, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/schedule/appointment/<int:appointment_id>', methods=['PUT'])
def update_appointment_route(appointment_id):
    """
    Updates an existing appointment.
    """
    try:
        data = request.get_json()
        response, status_code = handle_update_appointment(db, appointment_id, data)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

@app.route('/schedule/appointment/<int:appointment_id>', methods=['DELETE'])
def delete_appointment_route(appointment_id):
    """
    Deletes an existing appointment.
    """
    try:
        response, status_code = handle_delete_appointment(db, appointment_id)
        return jsonify(response), status_code
    except Exception as e:
        return jsonify({"status": "error", "message": f"Route error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)