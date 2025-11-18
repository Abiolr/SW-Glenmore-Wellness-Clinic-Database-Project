import pytest

def test_create_staff_shift(client):
    """Test POST /schedules/shifts."""
    # 1. Create a dummy staff member first to link the shift
    staff_res = client.post('/staff', json={
        "first_name": "Shift", "last_name": "Worker",
        "email": "shift@test.com", "phone": "555-1111"
    })
    staff_id = staff_res.json["staff_id"]

    # 2. Create the shift
    shift_data = {
        "staff_id": staff_id,
        "date": "2025-12-01",
        "start_time": "2025-12-01T08:00:00",
        "end_time": "2025-12-01T16:00:00",
        "role_for_shift": "Walk-in Physician"
    }
    
    response = client.post('/schedules/shifts', json=shift_data)
    assert response.status_code == 201
    data = response.json
    assert data["role_for_shift"] == "Walk-in Physician"
    assert "shift_id" in data

def test_get_daily_master_schedule(client):
    """Test GET /schedules/daily-master."""
    # 1. Setup data
    staff_res = client.post('/staff', json={
        "first_name": "Master", "last_name": "Schedule",
        "email": "master@test.com", "phone": "555-2222"
    })
    staff_id = staff_res.json["staff_id"]
    
    date_str = "2025-12-02"
    client.post('/schedules/shifts', json={
        "staff_id": staff_id,
        "date": date_str,
        "start_time": f"{date_str}T09:00:00",
        "end_time": f"{date_str}T17:00:00",
        "role_for_shift": "Midwife"
    })

    # 2. Fetch the schedule
    response = client.get(f'/schedules/daily-master?date={date_str}')
    assert response.status_code == 200
    data = response.json
    assert len(data) > 0
    assert data[0]["role_for_shift"] == "Midwife"

def test_get_daily_master_schedule_missing_date(client):
    """Test GET /schedules/daily-master without param."""
    response = client.get('/schedules/daily-master')
    assert response.status_code == 400

def test_get_staff_assignments(client):
    """Test GET /staff_assignments endpoint."""
    response = client.get('/staff_assignments')
    assert response.status_code == 200
    assert "assignments" in response.json
    assert response.json["status"] == "success"

def test_create_staff_assignment(client):
    """Test POST /staff_assignment endpoint."""
    new_assignment = {
        "date": "2025-11-15",
        "staff_name": "Test Nurse",
        "on_call_start": "08:00",
        "on_call_end": "16:00",
        "phone_number": "555-0101"
    }
    
    response = client.post('/staff_assignment', json=new_assignment)
    
    assert response.status_code == 201
    assert response.json["status"] == "success"
    assert response.json["assignment"]["staff_name"] == "Test Nurse"
    assert "assignment_id" in response.json["assignment"]

def test_create_staff_assignment_bad_request(client):
    """Test POST /staff_assignment with missing data."""
    bad_data = {
        "staff_name": "Incomplete Data"
    }
    response = client.post('/staff_assignment', json=bad_data)
    assert response.status_code == 400

def test_update_staff_assignment(client):
    """Test PUT /staff_assignment/<id> endpoint."""
    # 1. Create an assignment first
    create_data = {
        "date": "2025-11-16",
        "staff_name": "Update Me",
        "on_call_start": "09:00",
        "on_call_end": "17:00",
        "phone_number": "555-0102"
    }
    create_res = client.post('/staff_assignment', json=create_data)
    assignment_id = create_res.json["assignment"]["assignment_id"]
    
    # 2. Update the assignment
    update_data = {
        "staff_name": "Updated Name",
        "phone_number": "555-9999"
    }
    response = client.put(f'/staff_assignment/{assignment_id}', json=update_data)
    
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert response.json["assignment"]["staff_name"] == "Updated Name"
    assert response.json["assignment"]["phone_number"] == "555-9999"

def test_update_staff_assignment_not_found(client):
    """Test PUT /staff_assignment/<id> for non-existent ID."""
    response = client.put('/staff_assignment/999999', json={"staff_name": "Nobody"})
    assert response.status_code == 404

def test_delete_staff_assignment(client):
    """Test DELETE /staff_assignment/<id> endpoint."""
    # 1. Create an assignment first
    create_data = {
        "date": "2025-11-17",
        "staff_name": "Delete Me",
        "on_call_start": "10:00",
        "on_call_end": "12:00",
        "phone_number": "555-0103"
    }
    create_res = client.post('/staff_assignment', json=create_data)
    assignment_id = create_res.json["assignment"]["assignment_id"]
    
    # 2. Delete it
    response = client.delete(f'/staff_assignment/{assignment_id}')
    
    assert response.status_code == 200
    assert response.json["status"] == "success"

def test_delete_staff_assignment_not_found(client):
    """Test DELETE /staff_assignment/<id> for non-existent ID."""
    response = client.delete('/staff_assignment/999999')
    assert response.status_code == 404