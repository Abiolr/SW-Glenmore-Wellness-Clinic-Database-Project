import pytest

# --- Diagnosis ---

def test_get_diagnoses(client):
    response = client.get('/diagnoses')
    assert response.status_code == 200

def test_get_diagnosis_not_found(client):
    response = client.get('/diagnoses/99999')
    assert response.status_code == 404

def test_search_diagnoses_by_code(client):
    response = client.get('/diagnoses/search/Z99')
    assert response.status_code == 200

# --- Procedure ---

def test_get_procedures(client):
    response = client.get('/procedures')
    assert response.status_code == 200

def test_get_procedure_not_found(client):
    response = client.get('/procedures/99999')
    assert response.status_code == 404

# --- Drug ---

def test_get_drugs(client):
    response = client.get('/drugs')
    assert response.status_code == 200

def test_create_drug_bad_request(client):
    """Test POST /drugs with missing required fields."""
    response = client.post('/drugs', json={
        "generic_name": "Test-o-mol"
    })
    assert response.status_code == 400

def test_create_drug_success(client):
    """Test POST /drugs with correct fields."""
    drug_data = {
        "brand_name": "Test-Brand",
        "strength_form": "100mg tablet",
        "generic_name": "Test-o-mol"
    }
    response = client.post('/drugs', json=drug_data)
    
    # Check if creation was successful
    assert response.status_code == 201
    
    # Optionally, check if the returned data matches
    assert response.json["brand_name"] == "Test-Brand"

def test_get_drug_not_found(client):
    response = client.get('/drugs/99999')
    assert response.status_code == 404

def test_search_drugs_by_name(client):
    response = client.get('/drugs/search/NonExistentDrug')
    assert response.status_code == 200

# --- Prescription ---

def test_get_prescription_not_found(client):
    response = client.get('/prescriptions/99999')
    assert response.status_code == 404

def test_get_prescriptions_by_visit(client):
    response = client.get('/prescriptions/visit/99999')
    assert response.status_code == 200

# --- Lab Test Order ---

def test_get_lab_test_not_found(client):
    response = client.get('/lab-tests/99999')
    assert response.status_code == 404

def test_get_lab_tests_by_visit(client):
    response = client.get('/lab-tests/visit/99999')
    assert response.status_code == 200

# --- Delivery ---

def test_get_delivery_by_visit_not_found(client):
    response = client.get('/deliveries/visit/99999')
    assert response.status_code == 404

# --- Recovery Stay ---

def test_get_recovery_stay_not_found(client):
    response = client.get('/recovery-stays/99999')
    assert response.status_code == 404

# --- Recovery Observation ---

def test_get_recovery_observations_by_stay(client):
    response = client.get('/recovery-observations/stay/99999')
    assert response.status_code == 200