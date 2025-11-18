def test_create_staff(client):
    """Test POST /staff"""
    staff_data = {
        "first_name": "Dr. Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@clinic.com",
        "phone": "483-555-0101"
    }
    response = client.post('/staff', json=staff_data)
    assert response.status_code == 201
    data = response.json
    assert data["first_name"] == "Dr. Alice"
    assert data["email"] == "alice.johnson@clinic.com"
    assert "staff_id" in data

def test_get_staff(client):
    """Test GET /staff endpoint."""
    response = client.get('/staff')
    assert response.status_code == 200

def test_get_staff_active_only(client):
    """Test GET /staff?active_only=true endpoint."""
    response = client.get('/staff?active_only=true')
    assert response.status_code == 200

def test_get_staff_member_not_found(client):
    """Test GET /staff/<id> for a non-existent staff member."""
    response = client.get('/staff/99999')
    assert response.status_code == 404

def test_create_staff_bad_request(client):
    """Test POST /staff with no data."""
    response = client.post('/staff', json={})
    assert response.status_code == 400