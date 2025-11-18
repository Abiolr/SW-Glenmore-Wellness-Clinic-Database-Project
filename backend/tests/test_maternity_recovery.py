import pytest

def test_create_delivery(client):
    """Test POST /deliveries"""
    # Create mother patient, staff, and visit first
    mother = client.post('/patients', json={
        "first_name": "Mother", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-1111"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Delivery", "last_name": "Doctor",
        "email": "delivery@clinic.com", "phone": "483-555-1111"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": mother["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "prenatal",
        "start_time": "2025-11-20T14:00:00"
    })
    
    if visit.status_code == 201:
        visit_data = visit.json
        delivery_data = {
            "visit_id": visit_data["visit_id"],
            "performed_by": staff["staff_id"]
        }
        response = client.post('/deliveries', json=delivery_data)
        assert response.status_code in [201, 400]

def test_get_delivery_by_visit_not_found(client):
    response = client.get('/deliveries/visit/99999')
    assert response.status_code == 404

def test_create_recovery_stay(client):
    """Test POST /recovery-stays"""
    # Create patient, staff, and visit first
    patient = client.post('/patients', json={
        "first_name": "Recovery", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-2222"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Recovery", "last_name": "Nurse",
        "email": "recovery@clinic.com", "phone": "483-555-2222"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "postnatal",
        "start_time": "2025-11-20T15:00:00"
    })
    
    if visit.status_code == 201:
        visit_data = visit.json
        stay_data = {
            "patient_id": patient["patient_id"],
            "admit_time": "2025-11-20T14:30:00",
            "notes": "Post-delivery observation."
        }
        response = client.post('/recovery-stays', json=stay_data)
        assert response.status_code in [201, 400]

def test_get_recovery_stay_not_found(client):
    response = client.get('/recovery-stays/99999')
    assert response.status_code == 404

def test_create_recovery_observation(client):
    """Test POST /recovery-observations"""
    # Create recovery stay first
    patient = client.post('/patients', json={
        "first_name": "Observation", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-3333"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Observation", "last_name": "Nurse",
        "email": "observation@clinic.com", "phone": "483-555-3333"
    }).json
    
    visit = client.post('/visits', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "visit_type": "postnatal",
        "start_time": "2025-11-20T16:00:00"
    })
    
    stay = client.post('/recovery-stays', json={
        "patient_id": patient["patient_id"],
        "admit_time": "2025-11-20T16:30:00"
    })
    
    if stay.status_code == 201:
        stay_data = stay.json
        observation_data = {
            "stay_id": stay_data["stay_id"],
            "text_on": "2025-11-20T17:00:00",
            "notes": "Vitals stable. BP 120/80."
        }
        response = client.post('/recovery-observations', json=observation_data)
        assert response.status_code in [201, 400]

def test_get_recovery_observations_by_stay(client):
    response = client.get('/recovery-observations/stay/99999')
    assert response.status_code == 200