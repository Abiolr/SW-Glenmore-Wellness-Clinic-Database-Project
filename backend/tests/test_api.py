import pytest

def test_root(client):
    """Test GET /"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json["message"] == "SW Glenmore Wellness Clinic API"
    assert "version" in response.json
    assert response.json["status"] == "active"

def test_health_check(client):
    """Test GET /health"""
    response = client.get('/health')
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert response.json["status"] == "healthy"
        assert response.json["database"] == "connected"
    else:
        assert "error" in response.json