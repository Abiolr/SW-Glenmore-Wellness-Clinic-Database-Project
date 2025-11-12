# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from connection_DB import db
from weekly_coverage import *

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)