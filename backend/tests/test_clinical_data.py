import pytest

def test_create_diagnosis(client):
    """Test POST /diagnoses"""
    diagnosis_data = {
        "code": "J00",
        "description": "Acute nasopharyngitis (common cold)"
    }
    response = client.post('/diagnoses', json=diagnosis_data)
    assert response.status_code == 201
    data = response.json
    assert data["code"] == "J00"
    assert "diagnosis_id" in data

def test_get_diagnoses(client):
    response = client.get('/diagnoses')
    assert response.status_code == 200

def test_get_diagnosis_not_found(client):
    response = client.get('/diagnoses/99999')
    assert response.status_code == 404

def test_search_diagnoses_by_code(client):
    response = client.get('/diagnoses/search/J00')
    assert response.status_code == 200

def test_create_procedure(client):
    """Test POST /procedures"""
    procedure_data = {
        "code": "CONSULT",
        "description": "Standard Consultation",
        "default_fee": 150.00
    }
    response = client.post('/procedures', json=procedure_data)
    assert response.status_code == 201
    data = response.json
    assert data["code"] == "CONSULT"
    assert "procedure_id" in data

def test_get_procedures(client):
    response = client.get('/procedures')
    assert response.status_code == 200

def test_get_procedure_not_found(client):
    response = client.get('/procedures/99999')
    assert response.status_code == 404

def test_get_procedure_by_id(client):
    """Test GET /procedures/<int:procedure_id>"""
    # Create procedure first
    procedure = client.post('/procedures', json={
        "code": "BLOOD",
        "description": "Blood Test",
        "default_fee": 75.00
    }).json
    
    response = client.get(f'/procedures/{procedure["procedure_id"]}')
    assert response.status_code == 200
    assert response.json["procedure_id"] == procedure["procedure_id"]

def test_create_drug(client):
    """Test POST /drugs"""
    drug_data = {
        "brand_name": "Tylenol",
        "strength_form": "500mg tablet",
        "generic_name": "Acetaminophen"
    }
    response = client.post('/drugs', json=drug_data)
    assert response.status_code == 201
    data = response.json
    assert data["brand_name"] == "Tylenol"
    assert "drug_id" in data

def test_get_drugs(client):
    response = client.get('/drugs')
    assert response.status_code == 200

def test_get_drug_not_found(client):
    response = client.get('/drugs/99999')
    assert response.status_code == 404

def test_get_drug_by_id(client):
    """Test GET /drugs/<int:drug_id>"""
    # Create drug first
    drug = client.post('/drugs', json={
        "brand_name": "Advil",
        "strength_form": "200mg tablet",
        "generic_name": "Ibuprofen"
    }).json
    
    response = client.get(f'/drugs/{drug["drug_id"]}')
    assert response.status_code == 200
    assert response.json["drug_id"] == drug["drug_id"]

def test_search_drugs_by_name(client):
    response = client.get('/drugs/search/Tylenol')
    assert response.status_code == 200

def test_create_prescription(client):
    """Test POST /prescriptions"""
    # Create patient, staff, visit, and drug first
    patient = client.post('/patients', json={
        "first_name": "Prescription", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-1111"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Prescription", "last_name": "Doctor",
        "email": "prescription@clinic.com", "phone": "483-555-1111"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T10:00:00"
    })
    
    drug = client.post('/drugs', json={
        "brand_name": "Test Drug",
        "strength_form": "100mg tablet",
        "generic_name": "Test Generic"
    })
    
    if visit.status_code == 201 and drug.status_code == 201:
        visit_data = visit.json
        drug_data = drug.json
        prescription_data = {
            "visit_id": visit_data["visit_id"],
            "drug_id": drug_data["drug_id"],
            "name_on_label": "Test Drug 100mg"
        }
        response = client.post('/prescriptions', json=prescription_data)
        assert response.status_code in [201, 400]

def test_get_prescription_not_found(client):
    response = client.get('/prescriptions/99999')
    assert response.status_code == 404

def test_get_prescriptions_by_visit(client):
    response = client.get('/prescriptions/visit/99999')
    assert response.status_code == 200

def test_create_lab_test(client):
    """Test POST /lab-tests"""
    # Create patient, staff, and visit first
    patient = client.post('/patients', json={
        "first_name": "Lab", "last_name": "Test",
        "date_of_birth": "1990-01-01", "phone": "403-555-2222"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Lab", "last_name": "Doctor",
        "email": "lab@clinic.com", "phone": "483-555-2222"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T11:00:00"
    })
    
    if visit.status_code == 201:
        visit_data = visit.json
        lab_test_data = {
            "visit_id": visit_data["visit_id"],
            "ordered_by": staff["staff_id"],
            "test_name": "Complete Blood Count (CBC)"
        }
        response = client.post('/lab-tests', json=lab_test_data)
        assert response.status_code in [201, 400]

def test_get_lab_test_not_found(client):
    response = client.get('/lab-tests/99999')
    assert response.status_code == 404

def test_get_lab_tests_by_visit(client):
    response = client.get('/lab-tests/visit/99999')
    assert response.status_code == 200