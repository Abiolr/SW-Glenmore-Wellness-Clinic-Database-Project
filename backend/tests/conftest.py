import pytest
import sys
import os
from bson import ObjectId
import json

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom JSON encoder for ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

try:
    from app import app as flask_app
except ImportError:
    print("Error: 'app.py' not found. Make sure 'app.py' is in the parent directory of this 'tests' folder.")
    sys.exit(1)

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config['TESTING'] = True
    # You might want to configure a separate test database here
    # For example: flask_app.config['DATABASE_URI'] = 'mongodb://localhost:27017/test_clinic_db'
    
    # Set custom JSON encoder if needed
    if not hasattr(flask_app, 'json_encoder'):
        flask_app.json_encoder = JSONEncoder
    
    with flask_app.app_context():
        # This will use the app context created by the fixture
        pass

    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()