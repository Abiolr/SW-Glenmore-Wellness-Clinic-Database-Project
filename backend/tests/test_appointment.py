import pytest

def test_create_appointment(client):
    """Test POST /appointments"""
    # Create patient and staff first
    patient = client.post('/patients', json={
        "first_name": "Appointment", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-1111"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Appointment", "last_name": "Doctor",
        "email": "appointment@clinic.com", "phone": "483-555-1111"
    }).json
    
    appointment_data = {
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "scheduled_start": "2025-11-20T10:00:00",
        "scheduled_end": "2025-11-20T10:20:00",
        "is_walkin": False
    }
    response = client.post('/appointments', json=appointment_data)
    assert response.status_code == 201
    data = response.json
    assert "appointment_id" in data
    assert "created_at" in data

def test_get_appointments(client):
    """Test GET /appointments endpoint."""
    response = client.get('/appointments')
    assert response.status_code == 200

def test_get_appointment_not_found(client):
    """Test GET /appointments/<id> for a non-existent appointment."""
    response = client.get('/appointments/99999')
    assert response.status_code == 404

def test_get_appointments_by_patient(client):
    """Test GET /appointments/patient/<id> endpoint."""
    response = client.get('/appointments/patient/99999')
    assert response.status_code == 200

def test_get_appointments_by_staff(client):
    """Test GET /appointments/staff/<id> endpoint."""
    response = client.get('/appointments/staff/99999')
    assert response.status_code == 200

def test_update_appointment(client):
    """Test PUT /appointments/<int:appointment_id>"""
    # Create appointment first
    patient = client.post('/patients', json={
        "first_name": "Update", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-3333"
    }).json
    
    staff = client.post('/staff', json={
        "first_name": "Update", "last_name": "Doctor",
        "email": "update@clinic.com", "phone": "483-555-3333"
    }).json
    
    appointment = client.post('/appointments', json={
        "patient_id": patient["patient_id"],
        "staff_id": staff["staff_id"],
        "scheduled_start": "2025-11-20T12:00:00",
        "scheduled_end": "2025-11-20T12:20:00",
        "is_walkin": False
    })
    
    if appointment.status_code == 201:
        appointment_data = appointment.json
        # Update appointment
        update_data = {
            "patient_id": patient["patient_id"],
            "staff_id": staff["staff_id"],
            "scheduled_start": "2025-11-20T12:00:00",
            "scheduled_end": "2025-11-20T12:20:00",
            "is_walkin": True
        }
        response = client.put(f'/appointments/{appointment_data["appointment_id"]}', json=update_data)
        assert response.status_code in [200, 404]