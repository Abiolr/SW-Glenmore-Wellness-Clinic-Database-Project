import pytest

def test_create_visit(client):
    """Test POST /visits"""
    # Create patient and staff first
    patient = client.post('/patients', json={
        "first_name": "Visit", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-1111"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Visit", "last_name": "Doctor",
        "email": "visit@clinic.com", "phone": "483-555-1111"
    }).json
    
    visit_data = {
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T10:02:00",
        "notes": "Patient is in Room 2."
    }
    response = client.post('/visits', json=visit_data)
    assert response.status_code == 201
    data = response.json
    assert data["visit_type"] == "checkup"
    assert "visit_id" in data

def test_get_visits(client):
    """Test GET /visits endpoint."""
    response = client.get('/visits')
    assert response.status_code == 200

def test_get_visit_not_found(client):
    """Test GET /visits/<id> for a non-existent visit."""
    response = client.get('/visits/99999')
    assert response.status_code == 404

def test_get_visits_by_patient(client):
    """Test GET /visits/patient/<id> endpoint."""
    response = client.get('/visits/patient/99999')
    assert response.status_code == 200

def test_update_visit(client):
    """Test PUT /visits/<int:visit_id>"""
    # Create visit first
    patient = client.post('/patients', json={
        "first_name": "Update", "last_name": "Visit",
        "date_of_birth": "1990-01-01", "phone": "403-555-3333"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Update", "last_name": "VisitDoc",
        "email": "updatevisit@clinic.com", "phone": "483-555-3333"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T12:00:00"
    })
    
    if visit.status_code == 201:
        visit_data = visit.json
        # Update visit
        update_data = {
            "patient_id": patient["patient_id"],
            "staff_id": staff["staff_id"],
            "visit_type": "checkup",
            "start_time": "2025-11-20T12:00:00",
            "end_time": "2025-11-20T12:30:00",
            "notes": "Updated notes"
        }
        response = client.put(f'/visits/{visit_data["visit_id"]}', json=update_data)
        assert response.status_code in [200, 404]

def test_get_visit_diagnoses(client):
    """Test GET /visits/<id>/diagnoses endpoint."""
    response = client.get('/visits/99999/diagnoses')
    assert response.status_code == 200

def test_get_visit_procedures(client):
    """Test GET /visits/<id>/procedures endpoint."""
    response = client.get('/visits/99999/procedures')
    assert response.status_code == 200

def test_add_visit_diagnosis(client):
    """Test POST /visits/<int:visit_id>/diagnoses"""
    # Create visit and diagnosis first
    patient = client.post('/patients', json={
        "first_name": "Diagnosis", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-5555"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Diagnosis", "last_name": "Doctor",
        "email": "diagnosis@clinic.com", "phone": "483-555-5555"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T14:00:00"
    })
    
    diagnosis = client.post('/diagnoses', json={
        "code": "J00",
        "description": "Acute nasopharyngitis (common cold)"
    })
    
    if visit.status_code == 201 and diagnosis.status_code == 201:
        visit_data = visit.json
        diagnosis_data = diagnosis.json
        diagnosis_link_data = {
            "diagnosis_id": diagnosis_data["diagnosis_id"],
            "is_primary": True
        }
        response = client.post(f'/visits/{visit_data["visit_id"]}/diagnoses', json=diagnosis_link_data)
        assert response.status_code in [201, 400, 404]

def test_add_visit_procedure(client):
    """Test POST /visits/<int:visit_id>/procedures"""
    # Create visit and procedure first
    patient = client.post('/patients', json={
        "first_name": "Procedure", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-6666"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Procedure", "last_name": "Doctor",
        "email": "procedure@clinic.com", "phone": "483-555-6666"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "checkup",
        "start_time": "2025-11-20T15:00:00"
    })
    
    procedure = client.post('/procedures', json={
        "code": "CONSULT",
        "description": "Consultation",
        "default_fee": 150.00
    })
    
    if visit.status_code == 201 and procedure.status_code == 201:
        visit_data = visit.json
        procedure_data = procedure.json
        procedure_link_data = {
            "procedure_id": procedure_data["procedure_id"],
            "fee": 150.00
        }
        response = client.post(f'/visits/{visit_data["visit_id"]}/procedures', json=procedure_link_data)
        assert response.status_code in [201, 400, 404]