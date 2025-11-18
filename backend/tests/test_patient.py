import pytest

def test_create_patient(client):
    """Test POST /patients"""
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1985-04-12",
        "phone": "403-555-1234",
        "email": "john.doe@example.com",
        "address": "123 Main St SW, Calgary, AB",
        "emergency_contact": "Jane Doe",
        "emergency_phone": "403-555-5678"
    }
    response = client.post('/patients', json=patient_data)
    assert response.status_code == 201
    data = response.json
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "patient_id" in data

def test_get_patients(client):
    """Test GET /patients"""
    response = client.get('/patients')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_patients_with_pagination(client):
    """Test GET /patients with pagination"""
    response = client.get('/patients?skip=0&limit=10')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_patient_by_id(client):
    """Test GET /patients/<int:patient_id>"""
    # First create a patient
    patient_data = {
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01",
        "phone": "403-555-9999"
    }
    create_response = client.post('/patients', json=patient_data)
    patient_id = create_response.json["patient_id"]
    
    # Then get it
    response = client.get(f'/patients/{patient_id}')
    assert response.status_code == 200
    assert response.json["patient_id"] == patient_id

def test_get_patient_not_found(client):
    """Test GET /patients/<int:patient_id> for non-existent patient"""
    response = client.get('/patients/99999')
    assert response.status_code == 404

def test_update_patient(client):
    """Test PUT /patients/<int:patient_id>"""
    # Create patient first
    patient_data = {
        "first_name": "Update",
        "last_name": "Test",
        "date_of_birth": "1990-01-01",
        "phone": "403-555-1111"
    }
    create_response = client.post('/patients', json=patient_data)
    patient_id = create_response.json["patient_id"]
    
    # Update patient
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "date_of_birth": "1990-01-01",
        "phone": "403-555-2222"
    }
    response = client.put(f'/patients/{patient_id}', json=update_data)
    assert response.status_code == 200
    assert response.json["first_name"] == "Updated"

def test_delete_patient(client):
    """Test DELETE /patients/<int:patient_id>"""
    # Create patient first
    patient_data = {
        "first_name": "Delete",
        "last_name": "Test",
        "date_of_birth": "1990-01-01",
        "phone": "403-555-3333"
    }
    create_response = client.post('/patients', json=patient_data)
    patient_id = create_response.json["patient_id"]
    
    # Delete patient
    response = client.delete(f'/patients/{patient_id}')
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f'/patients/{patient_id}')
    assert get_response.status_code == 404

def test_search_patients_by_name(client):
    """Test GET /patients/search/by-name"""
    response = client.get('/patients/search/by-name?first_name=John&last_name=Doe')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_patient_bad_request(client):
    """Test POST /patients with invalid data"""
    response = client.post('/patients', json={})
    assert response.status_code == 400