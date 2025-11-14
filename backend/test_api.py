"""
Test script for the Wellness Clinic Flask API
Run this after starting the server to verify functionality
"""

import requests
import json
from datetime import datetime, date, timedelta

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200

def test_create_patient():
    """Test creating a patient"""
    patient_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1990-03-20",
        "phone": "403-555-0199",
        "email": "jane.smith@example.com",
        "gov_card_no": "GOV123456",
        "insurance_no": "INS987654"
    }
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print_response("Create Patient", response)
    if response.status_code == 201:
        return response.json()["patient_id"]
    return None

def test_get_patients():
    """Test getting all patients"""
    response = requests.get(f"{BASE_URL}/patients")
    print_response("Get All Patients", response)
    return response.status_code == 200

def test_create_staff():
    """Test creating a staff member"""
    staff_data = {
        "first_name": "Dr. Michael",
        "last_name": "Johnson",
        "email": "dr.johnson@clinic.com",
        "phone": "403-555-0200",
        "active": True
    }
    response = requests.post(f"{BASE_URL}/staff", json=staff_data)
    print_response("Create Staff", response)
    if response.status_code == 201:
        return response.json()["staff_id"]
    return None

def test_create_appointment(patient_id, staff_id):
    """Test creating an appointment"""
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_data = {
        "patient_id": patient_id,
        "staff_id": staff_id,
        "scheduled_start": tomorrow.replace(hour=10, minute=0, second=0).isoformat(),
        "scheduled_end": tomorrow.replace(hour=10, minute=10, second=0).isoformat(),
        "is_walkin": False
    }
    response = requests.post(f"{BASE_URL}/appointments", json=appointment_data)
    print_response("Create Appointment", response)
    if response.status_code == 201:
        return response.json()["appointment_id"]
    return None

def test_create_diagnosis():
    """Test creating a diagnosis"""
    diagnosis_data = {
        "code": "J00",
        "description": "Acute nasopharyngitis (common cold)"
    }
    response = requests.post(f"{BASE_URL}/diagnoses", json=diagnosis_data)
    print_response("Create Diagnosis", response)
    if response.status_code == 201:
        return response.json()["diagnosis_id"]
    return None

def test_create_procedure():
    """Test creating a procedure"""
    procedure_data = {
        "code": "99213",
        "description": "Office visit, established patient",
        "default_fee": 75.00
    }
    response = requests.post(f"{BASE_URL}/procedures", json=procedure_data)
    print_response("Create Procedure", response)
    if response.status_code == 201:
        return response.json()["procedure_id"]
    return None

def test_create_visit(patient_id, staff_id):
    """Test creating a visit"""
    visit_data = {
        "patient_id": patient_id,
        "staff_id": staff_id,
        "visit_type": "checkup",
        "start_time": datetime.now().isoformat(),
        "notes": "Annual checkup"
    }
    response = requests.post(f"{BASE_URL}/visits", json=visit_data)
    print_response("Create Visit", response)
    if response.status_code == 201:
        return response.json()["visit_id"]
    return None

def test_create_invoice(patient_id):
    """Test creating an invoice"""
    invoice_data = {
        "patient_id": patient_id,
        "invoice_date": date.today().isoformat(),
        "status": "pending"
    }
    response = requests.post(f"{BASE_URL}/invoices", json=invoice_data)
    print_response("Create Invoice", response)
    if response.status_code == 201:
        return response.json()["invoice_id"]
    return None

def test_search_patient(first_name):
    """Test searching for patients"""
    response = requests.get(f"{BASE_URL}/patients/search/by-name?first_name={first_name}")
    print_response(f"Search Patient by Name: {first_name}", response)
    return response.status_code == 200

def run_all_tests():
    """Run all test functions"""
    print("\n" + "="*50)
    print("WELLNESS CLINIC API TEST SUITE")
    print("="*50)
    
    try:
        # Test 1: Health Check
        print("\n[Test 1] Testing Health Check...")
        if not test_health_check():
            print("❌ Health check failed!")
            return
        print("✅ Health check passed!")
        
        # Test 2: Create Patient
        print("\n[Test 2] Testing Create Patient...")
        patient_id = test_create_patient()
        if not patient_id:
            print("❌ Create patient failed!")
            return
        print(f"✅ Patient created with ID: {patient_id}")
        
        # Test 3: Get All Patients
        print("\n[Test 3] Testing Get All Patients...")
        if not test_get_patients():
            print("❌ Get patients failed!")
            return
        print("✅ Get patients passed!")
        
        # Test 4: Create Staff
        print("\n[Test 4] Testing Create Staff...")
        staff_id = test_create_staff()
        if not staff_id:
            print("❌ Create staff failed!")
            return
        print(f"✅ Staff created with ID: {staff_id}")
        
        # Test 5: Create Appointment
        print("\n[Test 5] Testing Create Appointment...")
        appointment_id = test_create_appointment(patient_id, staff_id)
        if not appointment_id:
            print("❌ Create appointment failed!")
            return
        print(f"✅ Appointment created with ID: {appointment_id}")
        
        # Test 6: Create Diagnosis
        print("\n[Test 6] Testing Create Diagnosis...")
        diagnosis_id = test_create_diagnosis()
        if not diagnosis_id:
            print("❌ Create diagnosis failed!")
            return
        print(f"✅ Diagnosis created with ID: {diagnosis_id}")
        
        # Test 7: Create Procedure
        print("\n[Test 7] Testing Create Procedure...")
        procedure_id = test_create_procedure()
        if not procedure_id:
            print("❌ Create procedure failed!")
            return
        print(f"✅ Procedure created with ID: {procedure_id}")
        
        # Test 8: Create Visit
        print("\n[Test 8] Testing Create Visit...")
        visit_id = test_create_visit(patient_id, staff_id)
        if not visit_id:
            print("❌ Create visit failed!")
            return
        print(f"✅ Visit created with ID: {visit_id}")
        
        # Test 9: Create Invoice
        print("\n[Test 9] Testing Create Invoice...")
        invoice_id = test_create_invoice(patient_id)
        if not invoice_id:
            print("❌ Create invoice failed!")
            return
        print(f"✅ Invoice created with ID: {invoice_id}")
        
        # Test 10: Search Patient
        print("\n[Test 10] Testing Search Patient...")
        if not test_search_patient("Jane"):
            print("❌ Search patient failed!")
            return
        print("✅ Search patient passed!")
        
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✅")
        print("="*50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API.")
        print("Make sure the server is running at http://localhost:8000")
        print("Start it with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("Starting API tests...")
    print("Make sure the server is running: uvicorn main:app --reload")
    input("Press Enter to continue...")
    run_all_tests()
